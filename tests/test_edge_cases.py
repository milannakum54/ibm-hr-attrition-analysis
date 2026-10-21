"""Regressions discovered during the broader project audit."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import pytest
from src.data import prepare, group_rates, RAW_NAME
from src.statistics import statistical_checks, holm
from src.model import evaluate_models

RAW = Path(__file__).resolve().parents[1]/'data/raw'/RAW_NAME

def csv_path(tmp_path, frame):
    path = tmp_path/'sample.csv'
    frame.to_csv(path,index=False)
    return path

@pytest.mark.parametrize('column', ['DailyRate','HourlyRate','MonthlyRate','TotalWorkingYears'])
def test_invalid_constant_numeric_cannot_disappear_during_cleaning(tmp_path,column):
    frame = pd.read_csv(RAW).head(10)
    frame[column] = -1
    with pytest.raises(ValueError,match=column):
        prepare(csv_path(tmp_path,frame))

def test_duplicate_csv_headers_are_rejected(tmp_path):
    text = RAW.read_text(encoding='utf-8-sig')
    path=tmp_path/'duplicate.csv'
    path.write_text(text.replace('DailyRate','Age',1),encoding='utf-8')
    with pytest.raises(ValueError,match='Duplicate'):
        prepare(path)

def test_trailing_csv_field_is_rejected(tmp_path):
    lines=RAW.read_text(encoding='utf-8-sig').splitlines()
    lines[1] += ',extra'
    path=tmp_path/'ragged.csv'; path.write_text('\n'.join(lines),encoding='utf-8')
    with pytest.raises(ValueError,match='fields'):
        prepare(path)

def test_one_class_statistics_return_explicit_unavailable_results(tmp_path):
    frame=pd.read_csv(RAW).query("Attrition == 'No'").head(20)
    df,_=prepare(csv_path(tmp_path,frame))
    results=statistical_checks(df)
    assert len(results)==12
    assert (results.status=='not_testable').all()
    assert results.p_value.isna().all()

def test_constant_category_does_not_cancel_other_statistical_tests(tmp_path):
    frame=pd.read_csv(RAW).head(100)
    frame.Department='Sales'
    df,_=prepare(csv_path(tmp_path,frame))
    results=statistical_checks(df).set_index('feature')
    assert results.loc['Department','status']=='not_testable'
    assert results.loc['MonthlyIncome','status']=='ok'

@pytest.mark.parametrize('invalid', [[-.1],[1.1],[np.nan],[np.inf],[[.1,.2]]])
def test_holm_rejects_invalid_probabilities(invalid):
    with pytest.raises(ValueError):
        holm(invalid)

@pytest.mark.parametrize('label', ['n','left','rate_pct','small_group'])
def test_group_column_name_collision_has_clear_error(label):
    df=pd.DataFrame({label:['A','B'],'AttritionFlag':[0,1]})
    with pytest.raises(ValueError,match='reserved'):
        group_rates(df,label)

def test_one_class_model_has_clear_error(tmp_path):
    frame=pd.read_csv(RAW).query("Attrition == 'No'").head(20)
    df,_=prepare(csv_path(tmp_path,frame))
    with pytest.raises(ValueError,match='both attrition classes'):
        evaluate_models(df)
