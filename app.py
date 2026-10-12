import io
import pandas as pd
import streamlit as st
from engine import load_financials, assess_company, stress_test

st.set_page_config(page_title='Company Reality Checker', page_icon='🔎', layout='wide')
st.title('🔎 Company Reality Checker')
st.caption('Turn company financial statements into transparent warning signals and stress scenarios.')
st.info('Educational research tool, not financial advice. Metrics do not prove deception or predict stock returns.')

st.markdown('**Upload company-year financials (CSV)** or use the fictional demonstration dataset.')
upload = st.file_uploader('Upload CSV', type='csv')
try:
    if upload:
        raw = pd.read_csv(upload)
        origin = 'Uploaded dataset — verify source, reporting periods, and units.'
    else:
        raw = pd.read_csv(io.StringIO('''company,year,revenue,net_income,operating_cash_flow,debt,cash
Northstar Systems,2023,100,8,11,40,10
Northstar Systems,2024,125,10,12,42,13
Northstar Systems,2025,165,14,-4,62,9
Harbor Analytics,2023,100,15,18,20,24
Harbor Analytics,2024,115,18,22,18,30
Harbor Analytics,2025,131,20,25,16,38
Cedar Technologies,2024,50,-3,-1,35,5
Cedar Technologies,2025,53,-1,2,32,7'''))
        origin = 'FICTIONAL DEMONSTRATION DATA — not actual companies or filings.'
    data = load_financials(raw)
except (ValueError, pd.errors.ParserError, UnicodeDecodeError) as exc:
    st.error(f'Cannot read dataset: {exc}')
    st.stop()

st.warning(origin)
with st.expander('Required CSV columns and measurement rules'):
    st.code('company,year,revenue,net_income,operating_cash_flow,debt,cash')
    st.write('Use one row per fiscal year per company. Financial numbers must use the SAME currency and scale '
             'within each company (e.g. all USD millions). Debt and cash should be end-of-year values. '
             'Different fiscal year-ends, reporting standards, and definitions may make cross-company comparisons unreliable.')

company = st.selectbox('Choose a company', data.company.unique())
result = assess_company(data, company)

def pct(x):
    return 'N/A' if x is None else f'{x:.1%}'

st.subheader(f'{company} · {result["year"]}')
a,b,c,d = st.columns(4)
a.metric('Revenue', f'{result["revenue"]:,.2f}')
b.metric('Revenue growth', pct(result['revenue_growth']))
c.metric('Net margin', pct(result['net_margin']))
d.metric('Net debt', f'{result["net_debt"]:,.2f}')
st.caption('Numbers in source CSV units; growth requires consecutive years and prior revenue > 0.')

st.subheader('Evidence-based alerts')
if result['flags']:
    for title, explanation in result['flags']:
        st.warning(f'**{title}:** {explanation}')
else:
    st.success('No predefined alerts triggered. This does not mean the company is risk-free.')

history = result['history'].set_index('year')[['revenue', 'net_income', 'operating_cash_flow']]
st.subheader('Financial history')
st.line_chart(history)
st.dataframe(result['history'], hide_index=True, use_container_width=True)

st.subheader('What-if stress test')
st.caption('Independent assumptions, not a prediction: profit uses adjusted net margin; cash flow has its own shock.')
x,y,z = st.columns(3)
rev_change = x.slider('Revenue change (%)', -100, 100, -15, 5)
margin_change = y.slider('Net margin change (percentage points)', -30, 30, -3, 1)
cf_change = z.slider('Operating cash flow change (%)', -100, 100, -20, 5)
scenario = stress_test(result, rev_change, margin_change, cf_change)
c1,c2,c3 = st.columns(3)
c1.metric('Scenario revenue', f'{scenario["revenue"]:,.2f}')
c2.metric('Scenario net income', 'N/A' if scenario['net_income'] is None else f'{scenario["net_income"]:,.2f}')
c3.metric('Scenario operating cash flow', f'{scenario["operating_cash_flow"]:,.2f}')

st.subheader('Export reproducible results')
rows = [{ 'company': result['company'], 'year': result['year'],
          'revenue_growth': result['revenue_growth'], 'net_margin': result['net_margin'],
          'net_debt': result['net_debt'], 'alert_count': result['flag_count'],
          'alert_names': '; '.join(flag[0] for flag in result['flags']),
          'scenario_revenue': scenario['revenue'], 'scenario_net_income': scenario['net_income'],
          'scenario_operating_cash_flow': scenario['operating_cash_flow'] }]
st.download_button('Download analysis as CSV', pd.DataFrame(rows).to_csv(index=False).encode('utf-8'),
                   file_name='company_reality_analysis.csv', mime='text/csv')
