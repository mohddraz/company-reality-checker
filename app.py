"""Company Reality Checker — a Streamlit financial research prototype."""
import io
import html
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from engine import load_financials, assess_company, stress_test

st.set_page_config(page_title="Company Reality Checker | Studio", page_icon="◈", layout="wide", initial_sidebar_state="expanded")

STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root {--ink:#ebf2ff;--muted:#9dabbd;--line:#263849;--panel:#101e2c;--accent:#53dbc6;}
html,body,[class*="css"],.stApp{font-family:'DM Sans',sans-serif;}
.stApp {background: radial-gradient(ellipse at 82% -16%,#163e49 0%, transparent 39%), #08131e;color:var(--ink);}
[data-testid="stSidebar"]{background:#0b1925;border-right:1px solid var(--line);}
[data-testid="stHeader"]{background:transparent;}
.block-container{max-width:1450px;padding-top:2.5rem;padding-bottom:5rem;}
h1,h2,h3{font-family:'Manrope',sans-serif;letter-spacing:-.035em;}
h1{font-size:clamp(2.1rem,4vw,3.7rem)!important;font-weight:800!important;line-height:1.15!important;}
h2{font-size:1.55rem!important;} h3{font-size:1.15rem!important;}
p, label{color:#b7c5d4;}
.hero-eyebrow{color:#64dac9;font-size:.74rem;font-weight:800;letter-spacing:.16em;text-transform:uppercase;margin-bottom:10px;}
.hero-subtitle{color:#a8bac9;max-width:760px;font-size:1.04rem;line-height:1.6;}
.metric-tile{background:linear-gradient(148deg,#142738,#0f1d2b);border:1px solid #2a4050;border-radius:19px;padding:22px 23px;min-height:136px;animation:rise .42s ease both;transition:transform .22s ease,border-color .22s ease,box-shadow .22s ease;}
.metric-tile:hover{transform:translateY(-4px);border-color:#4e9b9d;box-shadow:0 12px 30px #0003;}
.metric-label{font-size:.76rem;color:#a8baca;margin-bottom:15px;letter-spacing:.02em;}
.metric-value{font-family:'Manrope',sans-serif;font-weight:800;font-size:clamp(1.3rem,2.5vw,2rem);letter-spacing:-.035em;color:#f3f7fd;}
.metric-note{font-size:.76rem;color:#86acbc;margin-top:7px;}
.section-kicker{color:#6fddcd;letter-spacing:.12em;text-transform:uppercase;font-size:.72rem;font-weight:800;margin-top:25px;margin-bottom:6px;}
.alert-card{border:1px solid #695333;border-left:4px solid #e2b06e;border-radius:13px;background:linear-gradient(90deg,#28241f,#18232d);padding:15px 18px;margin:10px 0;animation:rise .3s ease both;}
.alert-title{font-weight:800;color:#f4d3a1;margin-bottom:5px;}
.alert-detail{color:#c1c8ce;font-size:.9rem;line-height:1.5;}
.ok-card{border:1px solid #23594c;border-left:4px solid #50d9ab;border-radius:13px;background:#102923;padding:16px;color:#b9e8da;}
[data-testid="stDataFrame"], [data-testid="stPlotlyChart"]{border:1px solid #263b4c;border-radius:14px;overflow:hidden;}
.stButton>button,.stDownloadButton>button{border-radius:12px!important;border:1px solid #417b83!important;background:#153540!important;color:#dcfcf6!important;transition:transform .18s ease,background .18s ease;}
.stButton>button:hover,.stDownloadButton>button:hover{background:#20606a!important;transform:translateY(-2px);}
[data-baseweb="select"]>div,[data-testid="stFileUploader"]{border-radius:11px!important;}
@keyframes rise {from{opacity:0;transform:translateY(9px);}to{opacity:1;transform:translateY(0);}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation-duration:.01ms!important;transition-duration:.01ms!important;}}
@media(max-width:750px){.block-container{padding-top:1rem}.metric-tile{min-height:108px;padding:15px}}
</style>"""
st.markdown(STYLE, unsafe_allow_html=True)

DEMO = """company,year,revenue,net_income,operating_cash_flow,debt,cash
Northstar Systems,2023,100,8,11,40,10
Northstar Systems,2024,125,10,12,42,13
Northstar Systems,2025,165,14,-4,62,9
Harbor Analytics,2023,100,15,18,20,24
Harbor Analytics,2024,115,18,22,18,30
Harbor Analytics,2025,131,20,25,16,38
Cedar Technologies,2024,50,-3,-1,35,5
Cedar Technologies,2025,53,-1,2,32,7"""

def number(value):
    return f"{value:,.2f}"

def percent(value):
    return "Not available" if value is None else f"{value:+.1%}"

def metric(label, value, note=""):
    st.markdown(f'<div class="metric-tile"><div class="metric-label">{html.escape(str(label))}</div>'
                f'<div class="metric-value">{html.escape(str(value))}</div>'
                f'<div class="metric-note">{html.escape(str(note))}</div></div>',unsafe_allow_html=True)

def chart(frame, columns, title):
    chart_df = frame.sort_values("year")
    fig = go.Figure()
    shades = ["#58e2cd", "#869aff", "#f3bb72"]
    for idx,col in enumerate(columns):
        fig.add_trace(go.Scatter(x=chart_df["year"],y=chart_df[col],name=col.replace("_"," ").title(),
            mode="lines+markers",line=dict(color=shades[idx],width=3,shape="linear"),
            marker=dict(size=8,line=dict(width=2,color="#0d1c28")),
            hovertemplate="Year %{x}<br>Value %{y:,.2f}<extra>%{fullData.name}</extra>"))
    fig.update_layout(title=dict(text=title,font=dict(size=16,color="#ebf2ff")),
        paper_bgcolor="#101e2c",plot_bgcolor="#101e2c",font=dict(color="#adc2d1"),
        margin=dict(l=30,r=25,t=64,b=35),height=355,hovermode="x unified",
        legend=dict(orientation="h",y=-.2,x=0),
        xaxis=dict(tickmode="linear",dtick=1,showgrid=False,zeroline=False),
        yaxis=dict(gridcolor="#243747",zerolinecolor="#3d5162"),
        transition=dict(duration=300,easing="cubic-in-out"))
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

with st.sidebar:
    st.markdown('<div class="hero-eyebrow">◈ RESEARCH WORKSPACE</div>',unsafe_allow_html=True)
    st.title("Reality Checker")
    st.caption("Data-driven company research")
    st.divider()
    uploaded = st.file_uploader("Import company financials",type=["csv"],help="One company and fiscal year per row. Keep monetary units consistent.")
    if uploaded is None:
        raw = pd.read_csv(io.StringIO(DEMO))
        is_demo = True
    else:
        try:
            raw = pd.read_csv(uploaded)
        except (pd.errors.ParserError,UnicodeDecodeError,ValueError) as error:
            st.error(f"CSV cannot be read: {error}")
            st.stop()
        is_demo = False
    try:
        data = load_financials(raw)
    except ValueError as error:
        st.error(f"Invalid dataset: {error}")
        st.stop()
    company = st.selectbox("Company",data.company.unique())
    st.divider()
    st.caption("File format")
    with st.expander("CSV schema and units"):
        st.code("company,year,revenue,net_income,operating_cash_flow,debt,cash",language="text")
        st.write("One row per fiscal year. Use consistent currency and units, such as USD millions, for every number being compared. Debt and cash are year-end balances.")
        st.download_button("Download sample CSV",DEMO,file_name="sample_financials.csv",mime="text/csv")
    st.caption("Research prototype · Version 2.0")

result = assess_company(data,company)
st.markdown('<div class="hero-eyebrow">FINANCIAL INTELLIGENCE · V2.0</div>',unsafe_allow_html=True)
st.title("See beyond the headline numbers.")
st.markdown('<p class="hero-subtitle">Explore financial resilience, uncover mismatches between profit and cash flow, and test assumptions. Every signal traces back to measurable data.</p>',unsafe_allow_html=True)
if is_demo:
    st.warning("Illustrative demonstration data only. These companies and numbers are fictional, not actual filings.",icon="🧪")
else:
    st.info("Uploaded information: independently verify reporting periods, accounting definitions, units, and data sources.")
st.caption("Educational tool only · Not investment advice · Signals do not establish deception or predict stock returns.")

st.markdown('<div class="section-kicker">01 / SNAPSHOT</div>',unsafe_allow_html=True)
st.subheader(f"{company}  ·  FY {result['year']}")
a,b,c,d=st.columns(4)
with a: metric("Revenue",number(result["revenue"]),"Source dataset units")
with b: metric("Annual revenue growth",percent(result["revenue_growth"]),"Comparable consecutive years")
with c: metric("Net profit margin",percent(result["net_margin"]),"Net income ÷ revenue")
with d: metric("Net debt",number(result["net_debt"]),"Debt less cash")

st.markdown('<div class="section-kicker">02 / EVIDENCE SIGNALS</div>',unsafe_allow_html=True)
st.subheader("What deserves a closer look?")
if result["flags"]:
    for label,detail in result["flags"]:
        st.markdown(f'<div class="alert-card"><div class="alert-title">◉ {html.escape(label)}</div><div class="alert-detail">{html.escape(detail)}</div></div>',unsafe_allow_html=True)
else:
    st.markdown('<div class="ok-card">No predefined signals were triggered. This is not a guarantee of financial health.</div>',unsafe_allow_html=True)

st.markdown('<div class="section-kicker">03 / TRENDS</div>',unsafe_allow_html=True)
st.subheader("How has the business changed?")
view=st.segmented_control("View metrics",options=["Revenue & profit","Profit & cash flow"],default="Revenue & profit")
cols=["revenue","net_income"] if view=="Revenue & profit" else ["net_income","operating_cash_flow"]
chart(result["history"],cols,"Financial performance by fiscal year")
with st.expander("View underlying financial statements",expanded=False):
    st.dataframe(result["history"],hide_index=True,use_container_width=True)

st.markdown('<div class="section-kicker">04 / SCENARIO LAB</div>',unsafe_allow_html=True)
st.subheader("Change the assumptions. See what follows.")
st.caption("Illustrative, independent shocks—not a prediction. Operating cash flow is shocked independently of earnings.")
x,y,z=st.columns(3)
rev=x.slider("Revenue shock (%)",-100,100,-15,5)
margin=y.slider("Net margin change (percentage points)",-30,30,-3,1)
cf=z.slider("Operating cash-flow shock (%)",-100,100,-20,5)
scenario=stress_test(result,rev,margin,cf)
p,q,r=st.columns(3)
with p:metric("Scenario revenue",number(scenario["revenue"]),f"{rev:+d}% from baseline")
with q:metric("Scenario net income","Not available" if scenario["net_income"] is None else number(scenario["net_income"]),f"{margin:+d} pp margin change")
with r:metric("Scenario operating cash flow",number(scenario["operating_cash_flow"]),f"{cf:+d}% from baseline")

st.markdown('<div class="section-kicker">05 / EXPORT</div>',unsafe_allow_html=True)
st.subheader("Keep the analysis reproducible.")
rows=[{"company":result["company"],"year":result["year"],"data_kind":"demo" if is_demo else "user_upload",
       "revenue_growth":result["revenue_growth"],"net_margin":result["net_margin"],"net_debt":result["net_debt"],
       "alert_count":result["flag_count"],"alert_names":"; ".join(n for n,_ in result["flags"]),
       "scenario_revenue":scenario["revenue"],"scenario_net_income":scenario["net_income"],
       "scenario_operating_cash_flow":scenario["operating_cash_flow"]}]
st.download_button("↓ Download analysis CSV",pd.DataFrame(rows).to_csv(index=False).encode(),"company_reality_analysis.csv","text/csv")
st.caption("Source: provided CSV or clearly labeled fictional demo. No automated fact-check of uploaded data is performed.")
