"""Seeded randomized inputs plus invariants and independent calculations."""
import numpy as np
import pandas as pd
import pytest
from src.data import prepare, group_rates
from src.statistics import holm, statistical_checks

@pytest.mark.parametrize('seed',range(50))
def test_random_group_rates_match_manual_counts(seed):
    rng=np.random.default_rng(seed)
    size=int(rng.integers(1,1000))
    frame=pd.DataFrame({'group':rng.choice(['A','B','C','D'],size),'AttritionFlag':rng.integers(0,2,size)})
    table=group_rates(frame,'group').set_index('group')
    assert table.n.sum()==size
    assert table.left.sum()==frame.AttritionFlag.sum()
    for label in frame.group.unique():
        flags=frame.loc[frame.group==label,'AttritionFlag'].tolist()
        assert table.loc[label,'rate_pct']==pytest.approx(100*sum(flags)/len(flags))
        assert table.loc[label,'small_group']==(len(flags)<30)
    shuffled=group_rates(frame.sample(frac=1,random_state=seed),'group').set_index('group')
    pd.testing.assert_frame_equal(table,shuffled)

@pytest.mark.parametrize('seed',range(20))
def test_random_subsets_and_duplicates(raw_frame,tmp_path,seed):
    sample=raw_frame.sample(n=seed+1,random_state=seed)
    frame=pd.concat([sample,sample.iloc[[0]]],ignore_index=True)
    path=tmp_path/'data.csv'; frame.to_csv(path,index=False)
    original=path.read_bytes(); clean,audit=prepare(path)
    assert len(clean)==seed+1
    assert audit['duplicates_removed']==1
    assert clean.AttritionFlag.sum()==sample.Attrition.eq('Yes').sum()
    assert clean.AgeGroup.notna().all()
    assert path.read_bytes()==original

@pytest.mark.parametrize('seed',range(30))
def test_holm_against_independent_stepdown(seed):
    values=np.random.default_rng(seed).random(seed+1)
    adjusted=holm(values)
    pairs=sorted(enumerate(values),key=lambda p:p[1])
    expected=np.zeros(len(values)); running=0
    for rank,(original,p) in enumerate(pairs):
        running=max(running,(len(values)-rank)*p)
        expected[original]=min(1,running)
    np.testing.assert_allclose(adjusted,expected)
    assert (adjusted>=values).all() and (adjusted<=1).all()

@pytest.mark.parametrize('n',[29,30])
def test_small_group_threshold(n):
    frame=pd.DataFrame({'group':['A']*n,'AttritionFlag':[0]*n})
    assert bool(group_rates(frame,'group').small_group.iloc[0])==(n<30)

def test_holm_empty_and_ties():
    assert holm([]).size==0
    np.testing.assert_allclose(holm([.01,.01,1,0]),[.03,.03,1,0])

def test_unobserved_groups_not_reported_as_zero_people():
    frame=pd.DataFrame({'group':pd.Categorical(['A','A'],categories=['A','B']),'AttritionFlag':[0,1]})
    table=group_rates(frame,'group')
    assert table.group.tolist()==['A'] and table.n.tolist()==[2]

def test_mann_whitney_effect_matches_pairwise_count(prepared):
    frame=prepared.head(15).copy()
    result=statistical_checks(frame).set_index('feature').loc['MonthlyIncome']
    left=frame.loc[frame.AttritionFlag==1,'MonthlyIncome'].tolist()
    stayed=frame.loc[frame.AttritionFlag==0,'MonthlyIncome'].tolist()
    u=sum(1 if x>y else .5 if x==y else 0 for x in left for y in stayed)
    assert result.statistic==u
    assert result.effect==pytest.approx(2*u/(len(left)*len(stayed))-1)

def test_chi_square_perfect_association_and_effect(prepared):
    frame=prepared.head(20).copy()
    frame['Attrition']=['Yes']*10+['No']*10
    frame['AttritionFlag']=[1]*10+[0]*10
    frame['OverTime']=frame.Attrition
    row=statistical_checks(frame).set_index('feature').loc['OverTime']
    assert row.statistic==pytest.approx(20)
    assert row.effect==pytest.approx(1)

def test_all_equal_numeric_values_have_zero_effect_and_undefined_test(prepared):
    frame=prepared.head(20).copy(); frame.MonthlyIncome=100
    row=statistical_checks(frame).set_index('feature').loc['MonthlyIncome']
    assert pd.isna(row.p_value) and row.effect==0 and row.status=='not_testable'

def test_sparse_tables_flagged(prepared):
    result=statistical_checks(prepared.head(10))
    assert result.assumption_note.str.contains('Sparse').any()

def test_inconsistent_targets_cannot_produce_statistics(prepared):
    frame=prepared.head(20).copy(); frame.loc[0,'AttritionFlag']=1-frame.loc[0,'AttritionFlag']
    with pytest.raises(ValueError,match='disagree'): statistical_checks(frame)

@pytest.mark.parametrize('seed',range(40))
def test_mutated_csv_bytes_either_validate_or_fail_cleanly(raw_frame,tmp_path,seed):
    rng=np.random.default_rng(seed)
    payload=bytearray(raw_frame.head(12).to_csv(index=False).encode('utf-8'))
    for _ in range(int(rng.integers(1,8))):
        position=int(rng.integers(0,len(payload)))
        payload[position]=int(rng.integers(0,256))
    path=tmp_path/'mutated.csv'; path.write_bytes(payload)
    try:
        clean,audit=prepare(path)
    except ValueError:
        pass  # Malformed input should be rejected, without an internal crash.
    else:
        assert not clean.isna().any().any()
        assert set(clean.AttritionFlag).issubset({0,1})
        assert clean.AgeGroup.notna().all()
        assert audit['clean_rows']==len(clean)
    assert path.read_bytes()==payload

def test_ten_thousand_rows_preserve_denominators(raw_frame,tmp_path):
    frame=pd.concat([raw_frame]*7,ignore_index=True).head(10000).copy()
    frame['EmployeeNumber']=np.arange(1,len(frame)+1)
    path=tmp_path/'larger.csv'; frame.to_csv(path,index=False)
    clean,_=prepare(path)
    table=group_rates(clean,'Department')
    assert table.n.sum()==10000
    assert table.left.sum()==frame.Attrition.eq('Yes').sum()
