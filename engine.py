"""Auditable financial checks; all monetary values in consistent units."""
import pandas as pd

REQUIRED = ('company', 'year', 'revenue', 'net_income', 'operating_cash_flow', 'debt', 'cash')
NUMERIC = ('revenue', 'net_income', 'operating_cash_flow', 'debt', 'cash')


def load_financials(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame.copy()
    df.columns = [str(c).strip().lower().replace(' ', '_') for c in df.columns]
    missing = sorted(set(REQUIRED) - set(df.columns))
    if missing:
        raise ValueError('Missing required columns: ' + ', '.join(missing))
    df = df.loc[:, list(REQUIRED)].copy()
    df['company'] = df['company'].astype('string').str.strip()
    if df['company'].isna().any() or df['company'].eq('').any():
        raise ValueError('Company names must not be blank.')
    for col in ('year',) + NUMERIC:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    if df[['year', *NUMERIC]].isna().any().any():
        raise ValueError('All years and financial values must be numeric and nonblank.')
    if not df['year'].mod(1).eq(0).all() or not df['year'].between(1900, 2200).all():
        raise ValueError('Year must be a valid four-digit calendar year.')
    df['year'] = df['year'].astype(int)
    if df.duplicated(['company', 'year']).any():
        raise ValueError('Only one record per company and year is allowed.')
    if (df[['debt', 'cash']] < 0).any().any():
        raise ValueError('Debt and cash cannot be negative in this simplified model.')
    if (df['revenue'] < 0).any():
        raise ValueError('Revenue cannot be negative in this simplified model.')
    return df.sort_values(['company', 'year']).reset_index(drop=True)


def safe_ratio(numerator, denominator):
    return None if denominator is None or denominator <= 0 else numerator / denominator


def assess_company(frame: pd.DataFrame, company: str) -> dict:
    df = load_financials(frame)
    history = df[df.company.eq(company)]
    if history.empty:
        raise ValueError(f'Company not found: {company}')
    last = history.iloc[-1]
    previous = history.iloc[-2] if len(history) >= 2 else None
    growth = None
    if previous is not None and last.year - previous.year == 1:
        growth = safe_ratio(last.revenue - previous.revenue, previous.revenue)
    margin = safe_ratio(last.net_income, last.revenue)
    cash_conversion = safe_ratio(last.operating_cash_flow, last.net_income)
    net_debt = float(last.debt - last.cash)
    flags = []
    if growth is not None and growth > 0.15 and last.operating_cash_flow < 0:
        flags.append(('Growth without cash', 'Revenue grew over 15%, but operating cash flow is negative.'))
    if last.net_income > 0 and last.operating_cash_flow < 0:
        flags.append(('Profit versus cash gap', 'The company reports profit but negative operating cash flow.'))
    if margin is not None and margin < 0:
        flags.append(('Loss-making year', 'Net income is negative relative to revenue.'))
    if net_debt > 0 and last.operating_cash_flow <= 0:
        flags.append(('Debt and cash pressure', 'Net debt is positive and operating cash flow is not positive.'))
    if growth is None:
        flags.append(('Insufficient comparable history', 'A prior consecutive year with positive revenue is needed to calculate growth.'))
    # Flag count is a simple descriptive indicator, not a credit score or investment recommendation.
    return {
        'company': company, 'year': int(last.year), 'revenue': float(last.revenue),
        'net_income': float(last.net_income), 'operating_cash_flow': float(last.operating_cash_flow),
        'debt': float(last.debt), 'cash': float(last.cash),
        'revenue_growth': growth, 'net_margin': margin,
        'cash_conversion': cash_conversion, 'net_debt': net_debt,
        'flags': flags, 'flag_count': len(flags), 'history': history.copy()
    }


def stress_test(assessment: dict, revenue_change_pct: float, margin_change_pp: float, cashflow_change_pct: float) -> dict:
    """Illustrative static scenario: net income uses shocked sales and adjusted net margin.

    Operating cash flow is independently shocked; this is not a forecast or DCF.
    """
    revenue = assessment['revenue'] * (1 + revenue_change_pct / 100)
    if revenue < 0:
        raise ValueError('Revenue change cannot produce negative revenue.')
    prior_margin = assessment['net_margin']
    margin = None if prior_margin is None else prior_margin + margin_change_pp / 100
    net_income = None if margin is None else revenue * margin
    ocf = assessment['operating_cash_flow'] * (1 + cashflow_change_pct / 100)
    return {'revenue': revenue, 'net_margin': margin, 'net_income': net_income,
            'operating_cash_flow': ocf, 'net_debt': assessment['net_debt']}
