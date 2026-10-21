"""Milan's regression cases for valid subsets, age boundaries and rates."""
from pathlib import Path
import pandas as pd
import pytest
from src.data import prepare, group_rates, RAW_NAME
from src.categorical import categorical_plots

RAW = Path(__file__).resolve().parents[1]/'data'/'raw'/RAW_NAME


def save_sample(tmp_path, frame):
    path = tmp_path/'sample.csv'
    frame.to_csv(path, index=False)
    return path


def test_single_class_subset_keeps_required_columns(tmp_path):
    frame = pd.read_csv(RAW).query("Attrition == 'No'").head(8).copy()
    frame['Department'] = 'Sales'
    clean, audit = prepare(save_sample(tmp_path, frame))
    assert len(clean) == 8
    assert {'Attrition','Department'}.issubset(clean.columns)
    assert {'Attrition','Department'}.issubset(audit['retained_required_constants'])
    assert group_rates(clean,'Department').iloc[0].rate_pct == 0


def test_exact_duplicates_removed_before_id_conflict_check(tmp_path):
    frame = pd.read_csv(RAW).head(8)
    repeated = pd.concat([frame, frame.iloc[[0]]], ignore_index=True)
    clean, audit = prepare(save_sample(tmp_path, repeated))
    assert len(clean) == 8
    assert audit['duplicates_removed'] == 1


def test_age_bin_boundaries(tmp_path):
    frame = pd.read_csv(RAW).head(8).copy()
    frame['Age'] = [18,29,30,39,40,49,50,100]
    clean, _ = prepare(save_sample(tmp_path, frame))
    assert clean.AgeGroup.tolist() == ['18-29','18-29','30-39','30-39','40-49','40-49','50+','50+']


@pytest.mark.parametrize('column,value,message', [
    ('JobRole','   ','nonblank'), ('JobLevel',6,'levels 1 to 5'),
    ('Age',29.5,'whole years'), ('JobSatisfaction',5,'ratings 1 to 4'),
])
def test_invalid_values_rejected(tmp_path,column,value,message):
    frame = pd.read_csv(RAW).head(8).copy()
    if column == 'Age':
        frame[column] = frame[column].astype(float)
    frame.loc[0,column] = value
    with pytest.raises(ValueError,match=message):
        prepare(save_sample(tmp_path,frame))


@pytest.mark.parametrize('frame,message', [
    (pd.DataFrame({'group':[], 'AttritionFlag':[]}), 'empty'),
    (pd.DataFrame({'group':['A',None], 'AttritionFlag':[1,0]}), 'missing'),
    (pd.DataFrame({'group':['A','A'], 'AttritionFlag':[1,2]}), 'only 0 and 1'),
])
def test_rate_inputs_rejected(frame,message):
    with pytest.raises(ValueError,match=message):
        group_rates(frame,'group')


def test_only_categorical_figures_are_returned(tmp_path):
    clean, _ = prepare(RAW)
    unrelated = tmp_path/'09_correlation.png'
    unrelated.write_bytes(b'Existing partner figure')
    generated = categorical_plots(clean,tmp_path)
    assert {p.name[:2] for p in generated} == {'01','02','03','04','06','07','10'}
    assert all(p.is_file() for p in generated)
    assert unrelated.read_bytes() == b'Existing partner figure'
