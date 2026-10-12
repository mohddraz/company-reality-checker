"""Reality Checker 3: interactive finance research terminal with accessible motion."""
from __future__ import annotations
import html
import io
import json
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from engine import load_financials, assess_company, stress_test
from research import (
    demo_frame, make_sample_csv, company_table, company_timeline, data_quality,
    explain_signal, stress_grid, report_json, compare_periods, LABELS,
)

st.set_page_config(
    page_title='Reality Checker | Financial research terminal',
    page_icon='◈', layout='wide', initial_sidebar_state='expanded',
)

COLORS = {
    'bg': '#080C13', 'card': '#111924', 'card2': '#162131',
    'text': '#E8EDF5', 'muted': '#8E9DB0', 'lime': '#B3F36C',
    'cyan': '#69E5D6', 'blue': '#7B94FF', 'amber': '#F7C879',
    'red': '#FF8295', 'stroke': '#263244',
}

CSS = '''
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root {--bg:#080C13;--card:#111924;--line:#263244;--text:#E8EDF5;--sub:#92A0B3;--lime:#B3F36C;}
html, body, .stApp, [data-testid="stAppViewContainer"] {font-family:'DM Sans',sans-serif;}
.stApp {color:var(--text);background:radial-gradient(ellipse 55% 50% at 90% -10%,#193329 0%,transparent 75%),radial-gradient(ellipse 40% 35% at 1% 70%,#101e34 0%,transparent 95%),var(--bg);}
[data-testid="stHeader"]{background:transparent;}
[data-testid="stSidebar"]{background:#0D141E;border-right:1px solid var(--line);}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:.65rem;}
.block-container{max-width:1600px;padding:2rem 3rem 5rem;}
h1,h2,h3{font-family:'Space Grotesk',sans-serif;letter-spacing:-.045em;}
h1{font-size:clamp(2.7rem,4.5vw,4.7rem)!important;line-height:1.06!important;font-weight:700!important;}
h2{font-size:1.5rem!important;}
h3{font-size:1.08rem!important;}
p,label{color:#B4BFCD;}
[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:7px;background:#0D1520;border:1px solid #273447;padding:7px;border-radius:18px;flex-wrap:wrap;}
[data-testid="stTabs"] button[role="tab"]{font-family:'DM Sans',sans-serif;padding:10px 15px;border-radius:12px;font-weight:700;color:#B4BFCD;transition:color .2s,background .2s,transform .2s;}
[data-testid="stTabs"] button[aria-selected="true"]{background:#B3F36C!important;color:#0B1507!important;}
[data-testid="stTabs"] button[role="tab"]:hover{transform:translateY(-2px);color:#fff;}
[data-testid="stTabs"] [data-baseweb="tab-highlight"]{display:none;}
[data-testid="stMetric"]{background:linear-gradient(145deg,#162334,#101923);border:1px solid #293747;border-radius:18px;padding:20px;min-height:112px;}
[data-testid="stMetricValue"]{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:1.95rem;}
[data-testid="stMetricLabel"]{font-weight:600;color:#92A0B3;}
[data-testid="stPlotlyChart"]{border:1px solid #263244;border-radius:19px;overflow:hidden;background:#111924;}
[data-testid="stDataFrame"]{border:1px solid #263244;border-radius:16px;overflow:hidden;}
[data-testid="stExpander"]{border:1px solid #273447;border-radius:13px;background:#101923;}
.stButton>button,.stDownloadButton>button{border:1px solid #3B5B49;border-radius:11px;background:#1C3328;color:#D7FFC5;font-weight:700;transition:transform .18s,background .18s,box-shadow .18s;}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-2px);background:#294D35;box-shadow:0 8px 24px #0005;}
[data-baseweb="select"]>div,[data-testid="stFileUploader"]{border-radius:12px!important;}
.mini-label{font-size:.7rem;font-weight:800;letter-spacing:.17em;text-transform:uppercase;color:#B3F36C;margin:4px 0 14px;}
.logo{font-family:'Space Grotesk',sans-serif;font-weight:700;letter-spacing:-.06em;font-size:2.1rem;color:#E8EDF5;line-height:1.1;}
.logo span{color:#B3F36C;}
.side-caption{color:#8999AA;font-size:.85rem;margin:12px 0 20px;}
.hero{padding:32px 38px 34px;background:linear-gradient(120deg,#17261F,#131C28 55%,#101925);border:1px solid #35463B;border-radius:25px;position:relative;overflow:hidden;margin-bottom:24px;animation:enter .55s ease both;}
.hero:after{content:'◈';position:absolute;font-size:245px;color:#B3F36C;opacity:.065;right:35px;top:-75px;pointer-events:none;}
.hero-title{font-family:'Space Grotesk',sans-serif;font-size:clamp(2.3rem,4vw,4.2rem);font-weight:700;color:#F0F6FC;letter-spacing:-.06em;line-height:1.04;margin:12px 0;max-width:850px;}
.hero-title em{color:#B3F36C;font-style:normal;}
.hero-description{font-size:1.03rem;color:#A7B6C4;line-height:1.65;max-width:690px;}
.pill{display:inline-flex;align-items:center;border-radius:99px;background:#253B2C;color:#CFF7AA;border:1px solid #43643B;font-weight:800;letter-spacing:.1em;text-transform:uppercase;font-size:.67rem;padding:8px 13px;}
.section{display:flex;justify-content:space-between;align-items:center;gap:14px;margin:26px 0 13px;}
.section-name{color:#F2F6FA;font-family:'Space Grotesk',sans-serif;font-size:1.35rem;font-weight:700;letter-spacing:-.035em;}
.section-meta{color:#91A2B1;font-size:.8rem;text-transform:uppercase;letter-spacing:.1em;}
.kpi{height:165px;border:1px solid #2B3B4C;border-radius:19px;background:linear-gradient(145deg,#182738,#111B27);padding:22px;display:flex;flex-direction:column;justify-content:space-between;transition:transform .24s,box-shadow .24s,border-color .24s;animation:enter .5s ease both;}
.kpi:hover{transform:translateY(-5px);border-color:#608C63;box-shadow:0 13px 40px #0005;}
.kpi-head{display:flex;justify-content:space-between;font-size:.8rem;color:#9CAFC0;font-weight:700;}
.kpi-symbol{font-size:1.08rem;color:#B3F36C;}
.kpi-value{font-family:'Space Grotesk',sans-serif;font-size:clamp(1.7rem,2.45vw,2.6rem);font-weight:700;color:#F2F8FF;letter-spacing:-.05em;}
.kpi-foot{font-size:.72rem;color:#8B9FB0;}
.tile{background:#111B28;border:1px solid #273747;border-radius:17px;padding:20px;margin:7px 0;min-height:113px;transition:border-color .2s,transform .2s;}
.tile:hover{border-color:#729B70;transform:translateY(-2px);}
.tile-title{color:#EEF5FA;font-weight:800;font-size:.98rem;margin-bottom:6px;}
.tile-body{font-size:.86rem;color:#A3B5C4;line-height:1.5;}
.signal{border:1px solid #5E4A36;border-left:4px solid #F7C879;background:linear-gradient(90deg,#27251F,#151F2C);padding:18px 21px;border-radius:15px;margin-bottom:10px;animation:enter .3s ease both;}
.signal-head{font-size:1rem;font-weight:800;color:#FFE0A6;}
.signal-desc{font-size:.86rem;color:#BCC5C9;margin-top:7px;line-height:1.5;}
.proof{font-size:.8rem;color:#DCC79D;margin-top:8px;font-family:monospace;}
.note{border:1px solid #335241;background:#172C24;border-radius:13px;padding:15px 19px;color:#C3F5D6;font-size:.87rem;}
.ribbon{display:flex;gap:12px;flex-wrap:wrap;margin:15px 0 0;}
.ribbon span{background:#1D3030;border:1px solid #32564E;padding:8px 13px;border-radius:99px;color:#A5E4D0;font-size:.75rem;font-weight:700;}
.info-stripe{padding:12px 18px;border:1px solid #2C4151;border-radius:12px;background:#131E2B;color:#A5B5C7;font-size:.81rem;margin-bottom:13px;}
.center-muted{text-align:center;color:#7F92A4;padding:25px;}
@keyframes enter{from{transform:translateY(13px);opacity:0}to{transform:translateY(0);opacity:1}}
@media(max-width:900px){.block-container{padding:1rem .85rem 3rem}.hero{padding:24px}.kpi{height:144px;padding:15px}.hero:after{display:none}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{transition:none!important;animation:none!important;scroll-behavior:auto!important}}
</style>
'''
st.markdown(CSS, unsafe_allow_html=True)


def esc(value):
    return html.escape(str(value), quote=True)


def fmt_num(value, suffix=''):
    if value is None or pd.isna(value):
        return 'N/A'
    return f'{value:,.2f}{suffix}'


def fmt_pct(value, signed=False):
    if value is None or pd.isna(value):
        return 'N/A'
    return f'{value:+.1%}' if signed else f'{value:.1%}'


def section(title, descriptor):
    st.markdown(f'<div class="section"><span class="section-name">{esc(title)}</span><span class="section-meta">{esc(descriptor)}</span></div>',unsafe_allow_html=True)


def kpi(label, value, foot, symbol='↗'):
    st.markdown(f'<div class="kpi"><div class="kpi-head"><span>{esc(label)}</span><span class="kpi-symbol">{esc(symbol)}</span></div><div class="kpi-value">{esc(value)}</div><div class="kpi-foot">{esc(foot)}</div></div>',unsafe_allow_html=True)


def tile(title, detail):
    st.markdown(f'<div class="tile"><div class="tile-title">{esc(title)}</div><div class="tile-body">{esc(detail)}</div></div>',unsafe_allow_html=True)


def fig_base(height=380):
    figure=go.Figure()
    figure.update_layout(
        height=height, paper_bgcolor=COLORS['card'],plot_bgcolor=COLORS['card'],
        margin=dict(l=20,r=20,t=34,b=30), font=dict(family='DM Sans',size=12,color='#B8C6D3'),
        hoverlabel=dict(bgcolor='#203044',font_color='#FFFFFF',font_size=13),
        hovermode='x unified',legend=dict(orientation='h',y=-.22,x=0),
        xaxis=dict(showgrid=False,zeroline=False,linecolor='#344257'),
        yaxis=dict(gridcolor='#273446',zerolinecolor='#344257',tickformat=',.2f'),
        transition=dict(duration=350,easing='cubic-in-out'),
    )
    return figure


def line_chart(history, fields, title=None):
    figure=fig_base(375)
    palette=[COLORS['lime'],COLORS['blue'],COLORS['cyan'],COLORS['amber']]
    for index, field in enumerate(fields):
        figure.add_trace(go.Scatter(
            x=history['year'], y=history[field], name=LABELS.get(field,field),
            mode='lines+markers',line=dict(color=palette[index%len(palette)],width=3,shape='spline',smoothing=.35),
            marker=dict(size=9,line=dict(color='#0A121C',width=2)),
            fill='tozeroy' if len(fields)==1 else None,
            fillcolor='rgba(179,243,108,.07)' if len(fields)==1 else None,
            hovertemplate='%{x}: %{y:,.2f}<extra>%{fullData.name}</extra>',
        ))
    if title:
        figure.update_layout(title=dict(text=title,font=dict(size=15,color='#F0F5FB')))
    figure.update_xaxes(tickmode='linear',dtick=1)
    st.plotly_chart(figure,use_container_width=True,config={'displayModeBar':False})


def bar_chart(frame, field, names):
    subset=frame[frame.company.isin(names)].copy().sort_values(field)
    figure=fig_base(345)
    values=subset[field].fillna(0)
    palette=[COLORS['lime'] if v>=0 else COLORS['red'] for v in values]
    figure.add_trace(go.Bar(x=subset['company'],y=values,marker=dict(color=palette,line=dict(width=0)),
                            hovertemplate='%{x}<br>%{y:,.3f}<extra></extra>',width=.53))
    figure.update_layout(showlegend=False)
    st.plotly_chart(figure,use_container_width=True,config={'displayModeBar':False})


def scatter_chart(frame):
    figure=fig_base(390)
    for _,r in frame.iterrows():
        x=r.revenue_growth
        y=r.net_margin
        if pd.isna(x) or pd.isna(y):
            continue
        figure.add_trace(go.Scatter(x=[x*100],y=[y*100],name=r.company,mode='markers+text',
                                    text=[r.company],textposition='top center',
                                    marker=dict(size=max(16,min(42,12+r.revenue/8)),color=COLORS['lime'] if y>=0 else COLORS['red'],
                                                line=dict(width=2,color='#EDF5E8')),
                                    hovertemplate='Growth %{x:.1f}%<br>Margin %{y:.1f}%<extra>%{fullData.name}</extra>'))
    figure.update_layout(xaxis_title='Revenue growth (%)',yaxis_title='Net margin (%)',hovermode='closest',showlegend=False)
    figure.add_hline(y=0,line_color='#64738B',line_dash='dot')
    st.plotly_chart(figure,use_container_width=True,config={'displayModeBar':False})


def heatmap_chart(assessment, granularity=7):
    levels=list(range(-30,31,10)) if granularity==7 else list(range(-40,41,5))
    margins=list(range(-12,13,4)) if granularity==7 else list(range(-15,16,3))
    grid=stress_grid(assessment,levels,margins)
    figure=fig_base(390)
    figure.add_trace(go.Heatmap(z=grid.values,x=grid.columns,y=grid.index,
        colorscale=[[0,'#FF8295'],[.5,'#1D3240'],[1,'#B3F36C']],
        colorbar=dict(title='Net income'),
        hovertemplate='Revenue shock %{x:+.0f}%<br>Margin change %{y:+.0f} pp<br>Net income %{z:,.2f}<extra></extra>'))
    figure.update_layout(xaxis_title='Revenue change (%)',yaxis_title='Net margin change (pp)')
    st.plotly_chart(figure,use_container_width=True,config={'displayModeBar':False})


with st.sidebar:
    st.markdown('<div class="mini-label">◈ ANALYTICS STUDIO</div><div class="logo">REALITY<span>.</span><br>CHECKER</div><div class="side-caption">Financial intelligence, without the noise.</div>',unsafe_allow_html=True)
    st.divider()
    uploaded=st.file_uploader('Import financial statements',type=['csv'],help='CSV file with company-year statements and consistent monetary units.')
    if uploaded is not None:
        try:
            frame=load_financials(pd.read_csv(uploaded))
            demo=False
        except (ValueError,pd.errors.ParserError,UnicodeDecodeError) as error:
            st.error(f'Cannot load your financial file: {error}')
            st.stop()
    else:
        frame=demo_frame()
        demo=True
    names=list(frame.company.unique())
    selected=st.selectbox('Active company',names,index=0)
    st.caption(f'{len(names)} companies · {len(frame)} reporting periods')
    st.divider()
    with st.expander('Data schema & import instructions'):
        st.code('company,year,revenue,net_income,operating_cash_flow,debt,cash',language='text')
        st.caption('Use consistent units and reporting dates. Uploaded data is not validated against filings.')
        st.download_button('Download example dataset',make_sample_csv(),file_name='reality_checker_demo.csv',mime='text/csv')
    st.markdown('<div class="mini-label">RESEARCH STATUS</div>',unsafe_allow_html=True)
    if demo:
        st.warning('Fictional demonstration data')
    else:
        st.info('Custom dataset — not independently verified')
    st.caption('Version 3.0 • Interactive research workspace')
    st.caption('Educational analysis only. Not financial advice.')

assessment=assess_company(frame,selected)
history=company_timeline(frame,selected)
table=company_table(frame)

st.markdown('''<div class="hero">
<span class="pill">● LIVE WORKSPACE · VERSION 3.0</span>
<div class="hero-title">Understand the story.<br><em>Challenge the numbers.</em></div>
<div class="hero-description">An interactive company intelligence terminal. Explore financial fundamentals, compare companies, and stress-test the assumptions behind their performance.</div>
<div class="ribbon"><span>◈ Explainable signals</span><span>↗ Multi-company comparison</span><span>◇ Scenario laboratory</span><span>⬡ Reproducible reports</span></div>
</div>''',unsafe_allow_html=True)
if demo:
    st.markdown('<div class="info-stripe">◇ DEMONSTRATION MODE: All company names and financial numbers are fictional, not market data.</div>',unsafe_allow_html=True)
else:
    st.markdown('<div class="info-stripe">◇ DATA IMPORTED: Check original company filings, definitions, dates, and currency before making interpretations.</div>',unsafe_allow_html=True)

overview,compare,lab,data_tab,methods=st.tabs([
    '◈  Overview','↗  Compare','◇  Scenario Lab','⬡  Data Studio','ⓘ  Methodology'
])

with overview:
    section('Company snapshot', f'{selected} · FY {assessment["year"]}')
    c1,c2,c3,c4=st.columns(4)
    with c1:kpi('Revenue',fmt_num(assessment['revenue']),'Reporting-period sales','↗')
    with c2:kpi('Yearly growth',fmt_pct(assessment['revenue_growth'],True),'Compared with prior year','⌁')
    with c3:kpi('Net margin',fmt_pct(assessment['net_margin']),'Net income / revenue','◈')
    with c4:kpi('Net debt',fmt_num(assessment['net_debt']),'Debt − cash','⬡')
    section('Evidence signals',f'{assessment["flag_count"]} triggered')
    if assessment['flags']:
        for label,detail in assessment['flags']:
            st.markdown(f'<div class="signal"><div class="signal-head">◉ {esc(label)}</div><div class="signal-desc">{esc(detail)}</div><div class="proof">Evidence: {esc(explain_signal(assessment,label))}</div></div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="note">No predefined flags triggered. Absence of a flag does not establish business health or low risk.</div>',unsafe_allow_html=True)
    section('Performance timeline','Select a view')
    show=st.segmented_control('Financial metric',options=['Revenue / Profit','Profit / Cash flow','Debt / Cash','Margin / Growth'],default='Revenue / Profit')
    mapped={
        'Revenue / Profit':['revenue','net_income'],
        'Profit / Cash flow':['net_income','operating_cash_flow'],
        'Debt / Cash':['debt','cash'],
        'Margin / Growth':['net_margin','revenue_growth'],
    }
    line_chart(history,mapped[show])
    with st.expander('Inspect underlying rows'):
        st.dataframe(history,hide_index=True,use_container_width=True)
    section('Business interpretation','Context matters')
    a,b=st.columns(2)
    with a:tile('Growth',f"Latest annual revenue change: {fmt_pct(assessment['revenue_growth'],True)}. Growth alone does not indicate cash generation or profitability.")
    with b:tile('Cash generation',f"Operating cash flow is {fmt_num(assessment['operating_cash_flow'])}. Compare this with net income {fmt_num(assessment['net_income'])} before drawing conclusions.")

with compare:
    section('Company comparison','Multi-select workspace')
    compare_names=st.multiselect('Choose companies',names,default=names[:min(len(names),4)],max_selections=12)
    if not compare_names:
        st.info('Select at least one company to start your comparison.')
    else:
        subset=table[table.company.isin(compare_names)].copy()
        opts={'Revenue':'revenue','Net income':'net_income','Cash flow':'operating_cash_flow','Net debt':'net_debt','Revenue growth':'revenue_growth','Net profit margin':'net_margin'}
        field_label=st.segmented_control('Ranking metric',list(opts.keys()),default='Revenue')
        selected_field=opts[field_label]
        section(f'{field_label} by company','Hover to inspect')
        bar_chart(subset,selected_field,compare_names)
        section('Growth × profitability','Bubble size represents revenue')
        scatter_chart(subset)
        section('Comparison table','Latest year per company')
        cols=['company','year','revenue','net_income','operating_cash_flow','revenue_growth','net_margin','net_debt','signal_count']
        st.dataframe(subset[cols],hide_index=True,use_container_width=True)
        st.download_button('↓ Download comparison CSV',subset[cols].to_csv(index=False),file_name='company_comparison.csv',mime='text/csv')

with lab:
    section('Scenario laboratory','Interactive assumptions — not forecasts')
    st.markdown('<div class="info-stripe">Move sliders to stress-test financial outcomes. Cash flow is adjusted independently of revenue and earnings; this is a simplified sensitivity model.</div>',unsafe_allow_html=True)
    x,y,z=st.columns(3)
    with x:rev=st.slider('Revenue change (%)',-80,100,-15,5)
    with y:margin=st.slider('Net margin change (pp)',-30,30,-3,1)
    with z:cash=st.slider('Operating cash flow change (%)',-100,100,-20,5)
    scenario=stress_test(assessment,rev,margin,cash)
    section('Scenario results','Model output')
    p,q,r=st.columns(3)
    with p:kpi('Scenario revenue',fmt_num(scenario['revenue']),f'Revenue shock {rev:+d}%','↗')
    with q:kpi('Scenario net income',fmt_num(scenario['net_income']),f'Margin adjustment {margin:+d} pp','◇')
    with r:kpi('Scenario cash flow',fmt_num(scenario['operating_cash_flow']),f'Cash-flow shock {cash:+d}%','↝')
    section('Sensitivity map','Revenue × margin')
    detail=st.toggle('Show finer heatmap grid',value=False)
    heatmap_chart(assessment,13 if detail else 7)
    st.caption('A positive or negative simulated result is not a statement about what the company will actually earn.')
    section('Presets','Compare different assumptions')
    scenarios={
        'Baseline':(0,0,0),
        'Demand slowdown':(-25,-4,-20),
        'Margin expansion':(15,5,10),
        'Cash pressure':(5,0,-50),
        'Severe contraction':(-40,-10,-60),
    }
    preset_results=[]
    for name,(r_change,m_change,c_change) in scenarios.items():
        outcome=stress_test(assessment,r_change,m_change,c_change)
        preset_results.append({'Scenario':name,'Revenue':outcome['revenue'],'Net income':outcome['net_income'],'Operating cash flow':outcome['operating_cash_flow']})
    st.dataframe(pd.DataFrame(preset_results),hide_index=True,use_container_width=True)
    assumptions={'revenue':rev,'margin':margin,'cash_flow':cash}

with data_tab:
    section('Data studio','Audit inputs and export findings')
    section('Input records',f'{len(frame)} rows')
    st.dataframe(frame,hide_index=True,use_container_width=True)
    section('Data-quality checks','Structural diagnostics')
    issues=data_quality(frame)
    if issues:
        for warning in issues:
            st.warning(warning)
    else:
        st.success('No gaps or zero-revenue observations found in the provided periods. This does not verify source accuracy.')
    section('Period-to-period bridge','Select reporting years')
    years=history.year.astype(int).tolist()
    if len(years)>=2:
        a,b=st.columns(2)
        with a:first=st.selectbox('Beginning year',years,index=0)
        with b:last=st.selectbox('Ending year',years,index=len(years)-1)
        if first==last:
            st.info('Select different years to view changes.')
        else:
            changes=compare_periods(frame,selected,first,last)
            difference=pd.DataFrame([{'Metric':LABELS.get(key,key),'From':value['old'],'To':value['new'],'Change':value['difference']} for key,value in changes.items()])
            st.dataframe(difference,hide_index=True,use_container_width=True)
    else:
        st.info('Two reporting periods are required for this comparison.')
    section('Research export','Reproducible outputs')
    try:
        current_assumptions=assumptions
    except NameError:
        current_assumptions={'revenue':0,'margin':0,'cash_flow':0}
    report=report_json(frame,selected,current_assumptions,demo)
    c1,c2=st.columns(2)
    with c1:st.download_button('↓ Download research JSON',report,file_name='reality_checker_research.json',mime='application/json',use_container_width=True)
    with c2:st.download_button('↓ Download normalized CSV',frame.to_csv(index=False),file_name='normalized_financials.csv',mime='text/csv',use_container_width=True)
    with st.expander('Preview structured report'):
        st.json(json.loads(report))

with methods:
    section('Research methodology','Traceable by design')
    st.markdown('### What our signals mean')
    tile('Growth without cash','Revenue grew more than 15% from a consecutive year, but operating cash flow is negative. This warrants investigation, not an allegation.')
    tile('Profit versus cash gap','Net income is positive while operating cash flow is negative. Accounting accruals, working capital and other factors may explain the difference.')
    tile('Loss-making year','Reported net income is negative relative to positive revenue.')
    tile('Debt and cash pressure','Net debt is positive and operating cash flow is non-positive. A simplified indicator only; debt maturity, financing terms and assets are not assessed.')
    tile('Missing comparable history','No usable prior consecutive annual revenue data exists to compute annual growth.')
    st.markdown('### Key calculations')
    st.latex(r'\text{Revenue Growth}=\frac{R_t-R_{t-1}}{R_{t-1}}')
    st.latex(r'\text{Net Margin}=\frac{\text{Net Income}}{\text{Revenue}}')
    st.latex(r'\text{Net Debt}=\text{Debt}-\text{Cash}')
    st.latex(r'\text{Scenario Net Income}=\text{Scenario Revenue}\times\text{Adjusted Net Margin}')
    st.markdown('### Scope and limitations')
    st.write('This prototype does not obtain live market prices, forecast stock returns, detect fraud, compare accounting policies, or verify uploaded numbers against audited filings. Data from different companies must use compatible currencies, definitions, and accounting periods.')
    st.markdown('### Accessibility and responsible motion')
    st.write('Card motion is subtle, controls remain native and keyboard-operable, and reduced-motion preferences disable decorative animation. Charts use text labels and downloadable tables to keep results inspectable.')
    st.markdown('### Open-source research workflow')
    st.write('Every financial calculation is implemented in Python and can be unit tested. The source data, assumptions, and output can be exported for independent review.')

st.divider()
st.caption('◈ REALITY CHECKER 3.0 · Educational financial research software · No investment advice · Demo records are fictional')
