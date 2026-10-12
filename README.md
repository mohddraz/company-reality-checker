# Reality Checker 3.0

An interactive financial research workspace built with **Streamlit**, **Plotly** and **Pandas**.

## Features
- Five navigable sections: Overview, Compare, Scenario Lab, Data Studio, Methodology
- Interactive charts, company filters, company-by-company rankings, growth/profitability matrix
- Explainable signal flags derived directly from financial inputs
- What-if sliders, preset cases, two-dimensional net-income sensitivity heatmap
- Input validation, dataset QA warnings, year-to-year comparison, reproducible JSON and CSV exports
- Dark adaptive UI with hover states and `prefers-reduced-motion` compliance

## Run locally

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Test

```bash
python -m pytest -q
```

## Deploy
Upload all files and the `.streamlit/config.toml` folder to an existing Streamlit Community Cloud repository. Set `app.py` as the main file.

## Expected CSV schema

`company,year,revenue,net_income,operating_cash_flow,debt,cash`

One row per company per fiscal year. Currency and unit conventions must be consistent. The sample companies and records are wholly fictional. The tool never validates external filings or makes investment recommendations.

## Limits
Our red flags are predefined descriptive conditions, not proof of accounting issues, corporate misconduct, credit worthiness or future returns. Stress-test sliders are simplified hypothetical assumptions, not forecasts.
