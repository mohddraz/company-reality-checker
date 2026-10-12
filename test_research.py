import json
import pandas as pd
import pytest
from engine import assess_company
from research import (
    demo_frame, company_timeline, company_table, ratio_change,
    data_quality, stress_grid, report_json, compare_periods,
    explain_signal, compare_companies, finite_or_none,
)

def test_demo_company_count():
    assert len(company_table(demo_frame())) == 4

def test_demo_history_order():
    assert company_timeline(demo_frame(),'Cedar Technologies').year.tolist() == [2022,2023,2024,2025]

def test_ratio_no_zero_division():
    assert ratio_change(10,0) is None

def test_ratio_growth():
    assert ratio_change(12,10) == pytest.approx(.2)

def test_year_to_year_bridge():
    data=compare_periods(demo_frame(),'Cedar Technologies',2024,2025)
    assert data['revenue']['difference'] == pytest.approx(3)

def test_missing_year_validation():
    with pytest.raises(ValueError):
        compare_periods(demo_frame(),'Cedar Technologies',2015,2025)

def test_grid_shape():
    a=assess_company(demo_frame(),'Cedar Technologies')
    assert stress_grid(a,[-10,0,10],[-5,0,5]).shape==(3,3)

def test_grid_baseline_equals_profit():
    a=assess_company(demo_frame(),'Cedar Technologies')
    assert stress_grid(a,[0],[0]).iloc[0,0] == pytest.approx(-1)

def test_report_is_valid_json():
    report=json.loads(report_json(demo_frame(),'Cedar Technologies',demo=True))
    assert report['metrics']['net_debt'] == pytest.approx(25)
    assert report['data_type'] == 'fictional demonstration'

def test_explained_signal():
    a=assess_company(demo_frame(),'Cedar Technologies')
    assert '53.00' in explain_signal(a,'Loss-making year')

def test_clean_demo():
    assert data_quality(demo_frame()) == []

def test_comparison_filters():
    out=compare_companies(demo_frame(),['Harbor Analytics'])
    assert out.company.tolist()==['Harbor Analytics']

def test_finite():
    assert finite_or_none(float('inf')) is None

def test_blank_comparison():
    with pytest.raises(ValueError):
        compare_companies(demo_frame(),[])

def test_detect_year_gap():
    f=demo_frame()
    f=f[~((f.company=='Cedar Technologies') & (f.year==2023))]
    assert any('2023' in issue for issue in data_quality(f))
