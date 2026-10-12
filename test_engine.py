import pandas as pd
import pytest
from engine import load_financials, assess_company, safe_ratio, stress_test

@pytest.fixture
def sample():
    return pd.DataFrame([
        {'company':'Test','year':2024,'revenue':100,'net_income':10,'operating_cash_flow':12,'debt':30,'cash':5},
        {'company':'Test','year':2025,'revenue':120,'net_income':15,'operating_cash_flow':-2,'debt':40,'cash':8},
    ])

def test_growth_alerts(sample):
    r = assess_company(sample,'Test')
    assert r['revenue_growth'] == pytest.approx(.2)
    assert r['net_margin'] == pytest.approx(.125)
    assert r['net_debt'] == 32
    assert {x[0] for x in r['flags']} == {'Growth without cash','Profit versus cash gap','Debt and cash pressure'}

def test_unsorted(sample):
    assert assess_company(sample.iloc[::-1], 'Test')['year'] == 2025

def test_missing_column(sample):
    with pytest.raises(ValueError,match='Missing required'):
        load_financials(sample.drop(columns=['debt']))

def test_duplicate_row(sample):
    with pytest.raises(ValueError,match='Only one'):
        load_financials(pd.concat([sample, sample.iloc[[0]]]))

def test_blank_and_bad_year(sample):
    a=sample.copy(); a.loc[0,'company']=' '
    with pytest.raises(ValueError,match='blank'): load_financials(a)
    b=sample.astype({'year': 'float64'}); b.loc[0,'year']=2024.5
    with pytest.raises(ValueError,match='year'): load_financials(b)

def test_zero_prior_revenue(sample):
    sample.loc[0,'revenue']=0
    assert assess_company(sample,'Test')['revenue_growth'] is None

def test_missing_year(sample):
    sample.loc[0,'year']=2023
    assert assess_company(sample,'Test')['revenue_growth'] is None

def test_single_year(sample):
    assert assess_company(sample.iloc[[0]],'Test')['revenue_growth'] is None

def test_cash_and_debt_validation(sample):
    sample.loc[0,'cash']=-1
    with pytest.raises(ValueError,match='Debt and cash'): load_financials(sample)

def test_nonnumeric(sample):
    sample=sample.astype({'revenue': 'object'}); sample.loc[0,'revenue']='N/A'
    with pytest.raises(ValueError,match='numeric'): load_financials(sample)

def test_stress(sample):
    result = stress_test(assess_company(sample,'Test'), -10, -2, -20)
    assert result['revenue'] == pytest.approx(108)
    assert result['net_margin'] == pytest.approx(.105)
    assert result['net_income'] == pytest.approx(11.34)
    assert result['operating_cash_flow'] == pytest.approx(-1.6)

def test_safe_ratio():
    assert safe_ratio(2, 0) is None
    assert safe_ratio(4, 2) == 2

def test_unknown_company(sample):
    with pytest.raises(ValueError,match='not found'): assess_company(sample,'Other')
