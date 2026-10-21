"""Holdout isolation, unseen categories, reproducibility and metric consistency."""
import numpy as np
import pandas as pd
import pytest
from src.model import evaluate_models, split_model_data, build_pipeline

def test_split_is_disjoint_and_excludes_all_target_copies(prepared):
    frame=prepared.copy()
    frame['CopiedTarget']=frame.AttritionFlag
    frame['EmployeeNumber']=np.arange(len(frame))
    train,test,ytrain,ytest=split_model_data(frame)
    assert set(train.index).isdisjoint(test.index)
    assert len(train)==1176 and len(test)==294
    assert not {'CopiedTarget','Attrition','AttritionFlag','EmployeeNumber','AgeGroup'} & set(train)
    assert not any(c.endswith('Label') for c in train)
    assert set(ytrain)==set(ytest)=={0,1}

def test_scaler_uses_training_values_only_and_handles_unseen_categories(prepared):
    train,test,ytrain,_=split_model_data(prepared)
    model=build_pipeline().fit(train,ytrain)
    transform=model.named_steps['columntransformer']
    scaler=transform.named_transformers_['numeric'].named_steps['standardscaler']
    numeric=train.select_dtypes(include='number')
    np.testing.assert_allclose(scaler.mean_,numeric.mean().to_numpy())
    assert not np.allclose(scaler.mean_,prepared[numeric.columns].mean().to_numpy())
    changed=test.head(5).copy(); changed['JobRole']='Unseen role at prediction time'
    probabilities=model.predict_proba(changed)
    assert np.isfinite(probabilities).all()
    np.testing.assert_allclose(probabilities.sum(axis=1),1)

def test_model_metrics_reproducible_and_confusion_counts_consistent(prepared):
    first=evaluate_models(prepared); second=evaluate_models(prepared)
    pd.testing.assert_frame_equal(first,second)
    for row in first.itertuples():
        assert row.tn+row.fp+row.fn+row.tp==row.test_n
        assert row.recall==pytest.approx(row.tp/(row.tp+row.fn))
        assert row.accuracy==pytest.approx((row.tp+row.tn)/row.test_n)
        for value in [row.precision,row.recall,row.f1,row.roc_auc,row.accuracy]:
            assert np.isfinite(value) and 0<=value<=1
    baseline=first.set_index('model').loc['majority_baseline']
    assert baseline.recall==0 and baseline.roc_auc==.5

@pytest.mark.parametrize('size,minority',[(2,1),(4,2),(20,1),(100,2)])
def test_insufficient_minority_data_rejected(prepared,size,minority):
    frame=prepared.head(size).copy()
    frame['AttritionFlag']=[1]*minority+[0]*(size-minority)
    frame['Attrition']=frame.AttritionFlag.map({0:'No',1:'Yes'})
    with pytest.raises(ValueError,match='observations|both classes'):
        evaluate_models(frame)

def test_empty_model_input(prepared):
    with pytest.raises(ValueError,match='empty'): evaluate_models(prepared.head(0))

def test_model_refuses_inconsistent_target(prepared):
    frame=prepared.head(30).copy(); frame['AttritionFlag']=1-frame.AttritionFlag
    with pytest.raises(ValueError,match='disagree'): evaluate_models(frame)

def test_constant_predictors_still_have_finite_model_metrics(prepared):
    frame=prepared.head(40).copy()
    for col in frame:
        if col not in ['Attrition','AttritionFlag']:
            frame[col]=frame[col].iloc[0]
    metrics=evaluate_models(frame)
    assert np.isfinite(metrics[['precision','recall','f1','roc_auc','accuracy']].to_numpy()).all()

def test_no_predictors_is_rejected(prepared):
    with pytest.raises(ValueError,match='predictors'):
        evaluate_models(prepared[['Attrition','AttritionFlag']])
