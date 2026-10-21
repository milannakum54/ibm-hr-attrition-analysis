"""Check analytical correctness and reject ambiguous data."""
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from src.data import prepare, group_rates, RAW_NAME
from src.statistics import holm
from scipy.stats import spearmanr
from src.statistics import holm, statistical_checks, ORDINAL_TESTS

RAW = Path(__file__).resolve().parents[1]/'data'/'raw'/RAW_NAME

def test_group_rates_use_each_group_denominator():
    df = pd.DataFrame({'team':['A','A','B','B','B','B'], 'AttritionFlag':[1,0,1,0,0,0]})
    rates = group_rates(df,'team').set_index('team')
    assert rates.loc['A','rate_pct'] == 50
    assert rates.loc['B','rate_pct'] == 25

def test_real_sample_and_no_mutation():
    before = RAW.read_bytes()
    df, report = prepare(RAW)
    assert (report['raw_rows'], report['raw_columns']) == (1470,35)
    assert df.AttritionFlag.sum() == 237
    assert not {'EmployeeNumber','EmployeeCount','Over18','StandardHours'} & set(df)
    assert not df.AgeGroup.isna().any()
    assert RAW.read_bytes() == before

def test_invalid_target_is_rejected(tmp_path):
    df = pd.read_csv(RAW); df.loc[0,'Attrition'] = 'Maybe'
    path = tmp_path/'bad.csv'; df.to_csv(path,index=False)
    with pytest.raises(ValueError, match='Attrition must'):
        prepare(path)

def test_conflicting_employee_is_rejected(tmp_path):
    df = pd.read_csv(RAW); df.loc[1,'EmployeeNumber'] = df.loc[0,'EmployeeNumber']
    path = tmp_path/'bad.csv'; df.to_csv(path,index=False)
    with pytest.raises(ValueError, match='Conflicting'):

def test_ordinal_trend_tests_match_scipy(prepared):
    result = statistical_checks(prepared).set_index('feature')
    for col in ORDINAL_TESTS:
        row = result.loc[col + ' (trend)']
        rho, p = spearmanr(prepared[col], prepared.AttritionFlag)
        assert row.test == 'Spearman' and row.status == 'ok'
        assert row.effect == pytest.approx(rho)
        assert row.p_value == pytest.approx(p)

def test_ordinal_trend_tests_are_in_holm_family(prepared):
    ok = statistical_checks(prepared).query("status == 'ok'")
    assert (ok.test == 'Spearman').sum() == 4
    np.testing.assert_allclose(ok.p_holm, holm(ok.p_value))
    assert (ok.p_holm >= ok.p_value - 1e-12).all()

def test_constant_ordinal_column_is_not_testable(prepared):
    frame = prepared.copy(); frame['JobLevel'] = 1
    row = statistical_checks(frame).set_index('feature').loc['JobLevel (trend)']
    assert row.status == 'not_testable' and np.isnan(row.p_value)
        prepare(path)

def test_holm_known_example():
    np.testing.assert_allclose(holm([.04,.01,.03]), [.06,.03,.06])
