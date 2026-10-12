# Company Reality Checker

An original educational finance research prototype, not an investment recommendation.

## Start on Windows

```powershell
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

## CSV format

`company,year,revenue,net_income,operating_cash_flow,debt,cash`

Use the same currency and number scale per company (e.g., USD millions). 1 row per fiscal year per company. Use authentic audited filings or statements and document their source.

## Test the logic

```powershell
py -m pytest -q
```

## Design limitations

- Flags are transparent heuristics, not evidence of fraud or an investing recommendation.
- Net income differs from operating cash flow for many legitimate reasons.
- Profit margin and revenue growth can be misleading across different industries and accounting standards.
- Scenario controls are independent and do not model economic causality, valuation, or probability.
- The included sample company data is fictional.
- No live market data is accessed; upload real filings for real analysis.
