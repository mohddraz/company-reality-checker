# Company Reality Checker v2.0

A polished research prototype for transparent company financial checks and stress tests.

## Start

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## What changed in v2
- Dark responsive dashboard and subtle CSS micro-interactions with reduced-motion support
- Interactive Plotly financial trend charts
- Sidebar workspace, downloadable demonstration dataset
- Evidence-based alerts, scenario controls, CSV export
- Same separately tested financial calculations (`engine.py`)

**Data caution:** All built-in company figures are fictional. Uploaded CSVs need independent source verification. Financial signals do not prove deception or predict future market behavior.

CSV schema: `company,year,revenue,net_income,operating_cash_flow,debt,cash`.
