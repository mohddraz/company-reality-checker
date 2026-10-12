"""Pure comparison, scenario, and research functions used by the interface."""
from __future__ import annotations
import io
import json
import math
from dataclasses import dataclass
import pandas as pd
from engine import assess_company, load_financials, stress_test

DEMO = '''company,year,revenue,net_income,operating_cash_flow,debt,cash
Northstar Systems,2022,82,7,9,36,8
Northstar Systems,2023,100,8,11,40,10
Northstar Systems,2024,125,10,12,42,13
Northstar Systems,2025,165,14,-4,62,9
Harbor Analytics,2022,91,12,16,23,19
Harbor Analytics,2023,100,15,18,20,24
Harbor Analytics,2024,115,18,22,18,30
Harbor Analytics,2025,131,20,25,16,38
Cedar Technologies,2022,44,-4,-2,39,4
Cedar Technologies,2023,47,-2,-2,37,4
Cedar Technologies,2024,50,-3,-1,35,5
Cedar Technologies,2025,53,-1,2,32,7
Orion Retail,2022,75,6,7,34,9
Orion Retail,2023,81,7,8,32,12
Orion Retail,2024,79,4,3,34,11
Orion Retail,2025,91,5,6,31,13'''

LABELS = {
    'revenue':'Revenue', 'net_income':'Net income',
    'operating_cash_flow':'Operating cash flow', 'debt':'Debt',
    'cash':'Cash', 'net_debt':'Net debt', 'net_margin':'Net margin',
    'revenue_growth':'Revenue growth', 'cash_conversion':'Cash conversion'
}


def demo_frame():
    return load_financials(pd.read_csv(io.StringIO(DEMO)))


def finite_or_none(value):
    if value is None:
        return None
    try:
        f = float(value)
        return f if math.isfinite(f) else None
    except (TypeError, ValueError):
        return None


def ratio_change(current, previous):
    """Growth is undefined if the previous measurement is not positive."""
    previous = finite_or_none(previous)
    current = finite_or_none(current)
    if previous is None or current is None or previous <= 0:
        return None
    return (current - previous) / previous


def company_timeline(frame, company):
    data = load_financials(frame)
    part = data[data.company == company].copy().sort_values('year')
    if part.empty:
        raise ValueError('Unknown company')
    part['net_margin'] = part.apply(lambda r: r.net_income / r.revenue if r.revenue > 0 else float('nan'), axis=1)
    part['net_debt'] = part.debt - part.cash
    part['revenue_growth'] = [float('nan')] + [
        ratio_change(part.iloc[i].revenue, part.iloc[i-1].revenue)
        if int(part.iloc[i].year) - int(part.iloc[i-1].year) == 1 else None
        for i in range(1, len(part))
    ]
    return part


def company_table(frame):
    data = load_financials(frame)
    results = []
    for company in data.company.unique():
        assessment = assess_company(data, company)
        results.append({
            'company': company,
            'year': assessment['year'],
            'revenue': assessment['revenue'],
            'net_income': assessment['net_income'],
            'operating_cash_flow': assessment['operating_cash_flow'],
            'revenue_growth': assessment['revenue_growth'],
            'net_margin': assessment['net_margin'],
            'net_debt': assessment['net_debt'],
            'signal_count': assessment['flag_count'],
        })
    return pd.DataFrame(results).sort_values('company').reset_index(drop=True)


def explain_signal(assessment, label):
    """Ground displayed evidence in numerical inputs, without claiming fraud."""
    if label == 'Growth without cash':
        return f"Annual revenue growth is {assessment['revenue_growth']:.1%}; operating cash flow is {assessment['operating_cash_flow']:,.2f}."
    if label == 'Profit versus cash gap':
        return f"Net income is {assessment['net_income']:,.2f}; operating cash flow is {assessment['operating_cash_flow']:,.2f}."
    if label == 'Loss-making year':
        return f"Net income is {assessment['net_income']:,.2f} on revenue of {assessment['revenue']:,.2f}."
    if label == 'Debt and cash pressure':
        return f"Debt less cash is {assessment['net_debt']:,.2f}; operating cash flow is {assessment['operating_cash_flow']:,.2f}."
    return 'Comparable financial history was not available for this signal.'


def stress_grid(assessment, revenue_shocks, margin_shocks):
    rows=[]
    for margin in margin_shocks:
        row=[]
        for revenue in revenue_shocks:
            outcome=stress_test(assessment,float(revenue),float(margin),0)
            row.append(outcome['net_income'])
        rows.append(row)
    return pd.DataFrame(rows,index=list(margin_shocks),columns=list(revenue_shocks))


def compare_companies(frame, names):
    tbl=company_table(frame)
    result=tbl[tbl.company.isin(names)].copy()
    if result.empty:
        raise ValueError('Choose a company to compare')
    return result


def data_quality(frame):
    data=load_financials(frame)
    warnings=[]
    for company, grp in data.groupby('company'):
        years=sorted(grp.year.astype(int).tolist())
        missing=[y for y in range(years[0],years[-1]+1) if y not in years]
        if missing:
            warnings.append(f'{company}: missing fiscal years {", ".join(map(str,missing))}.')
        if (grp.revenue == 0).any():
            warnings.append(f'{company}: zero revenue makes some ratios unavailable.')
    return warnings


def report_dict(frame, company, assumptions=None, demo=False):
    a=assess_company(frame,company)
    assumptions=assumptions or {'revenue':0,'margin':0,'cash_flow':0}
    s=stress_test(a, assumptions['revenue'],assumptions['margin'],assumptions['cash_flow'])
    return {
        'title':'Company Reality Checker — Research Export',
        'company':company,'fiscal_year':a['year'],
        'data_type':'fictional demonstration' if demo else 'user-supplied; independently unverified',
        'metrics':{k:a[k] for k in ('revenue','net_income','operating_cash_flow','cash','debt','net_debt','revenue_growth','net_margin')},
        'signals':[{'title':label,'description':desc,'evidence':explain_signal(a,label)} for label,desc in a['flags']],
        'assumptions':assumptions,'scenario':s,
        'limitations':['Not investment advice','Not an accusation or a fraud detector',
                       'User supplied numbers have not been audited','Scenarios are simplified independent shocks']
    }


def report_json(frame, company, assumptions=None, demo=False):
    return json.dumps(report_dict(frame,company,assumptions,demo),indent=2,allow_nan=False)


def make_sample_csv():
    return DEMO


def compare_periods(frame, company, from_year, to_year):
    data=company_timeline(frame,company).set_index('year')
    if from_year not in data.index or to_year not in data.index:
        raise ValueError('Both reporting periods must exist')
    old=data.loc[from_year]
    new=data.loc[to_year]
    metrics={}
    for key in ('revenue','net_income','operating_cash_flow','debt','cash','net_debt'):
        metrics[key]={'old':float(old[key]),'new':float(new[key]),'difference':float(new[key]-old[key])}
    return metrics
