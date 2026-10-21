"""Exploratory association tests with effect sizes and Holm adjustment."""
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, mannwhitneyu, spearmanr
from .data import validate_prepared

CATEGORICAL_TESTS = ['OverTime', 'Department', 'JobRole', 'JobLevel', 'JobSatisfaction',
                     'EnvironmentSatisfaction', 'WorkLifeBalance', 'BusinessTravel']
NUMERIC_TESTS = ['Age', 'MonthlyIncome', 'YearsAtCompany', 'DistanceFromHome']
ORDINAL_TESTS = ['JobLevel', 'JobSatisfaction', 'EnvironmentSatisfaction', 'WorkLifeBalance']

def holm(pvalues):
    values = np.asarray(pvalues, dtype=float)
    if values.ndim != 1 or not np.isfinite(values).all() or ((values<0)|(values>1)).any():
        raise ValueError('p-values must be a finite one-dimensional sequence between 0 and 1.')
    if not len(values):
        return values.copy()
    order = np.argsort(values)
    adjusted = np.minimum(1, np.maximum.accumulate(values[order] * (len(values)-np.arange(len(values)))))
    result = np.empty(len(values)); result[order] = adjusted
    return result

def statistical_checks(df):
    validate_prepared(df, CATEGORICAL_TESTS+NUMERIC_TESTS)
    rows = []
    for col in CATEGORICAL_TESTS:
        table = pd.crosstab(df[col], df.Attrition)
        table = table.loc[table.sum(axis=1)>0, table.sum(axis=0)>0]
        if min(table.shape) < 2:
            rows.append({'feature':col, 'test':'Chi-square', 'status':'not_testable',
                         'statistic':np.nan,'p_value':np.nan,'effect_name':'Cramers V','effect':np.nan,
                         'assumption_note':'Need at least two observed groups and both attrition classes.'})
            continue
        statistic, p, dof, expected = chi2_contingency(table, correction=False)
        rows.append({'feature':col, 'test':'Chi-square', 'status':'ok', 'statistic':statistic, 'p_value':p,
                     'effect_name':'Cramers V', 'effect':np.sqrt(statistic/(table.to_numpy().sum()*min(table.shape[0]-1, table.shape[1]-1))),
                     'assumption_note':'Sparse expected counts; asymptotic p-value requires caution' if (expected<5).any() else 'All expected counts >= 5'})
    for col in ORDINAL_TESTS:
        values = pd.to_numeric(df[col].astype(object), errors='coerce')
        usable = values.notna()
        effect_name = 'Spearman rho (positive = higher level, more attrition)'
        if usable.sum() < 3 or values[usable].nunique() < 2 or df.loc[usable, 'AttritionFlag'].nunique() < 2:
            rows.append({'feature':col + ' (trend)', 'test':'Spearman', 'status':'not_testable',
                         'statistic':np.nan, 'p_value':np.nan, 'effect_name':effect_name, 'effect':np.nan,
                         'assumption_note':'Need at least three observations, two ordinal levels and both attrition classes.'})
            continue
        rho, p = spearmanr(values[usable], df.loc[usable, 'AttritionFlag'])
        rows.append({'feature':col + ' (trend)', 'test':'Spearman', 'status':'ok',
                     'statistic':rho, 'p_value':p, 'effect_name':effect_name, 'effect':rho,
                     'assumption_note':'Monotonic trend test; ties in the ordinal scale use average ranks.'})
    for col in NUMERIC_TESTS:
        left = df.loc[df.AttritionFlag==1, col]
        stayed = df.loc[df.AttritionFlag==0, col]
        if left.empty or stayed.empty:
            rows.append({'feature':col,'test':'Mann-Whitney U','status':'not_testable',
                         'statistic':np.nan,'p_value':np.nan,'effect_name':'Rank-biserial (positive = leavers higher)',
                         'effect':np.nan,'assumption_note':'Both attrition classes are required.'})
            continue
        if df[col].nunique() < 2:
            rows.append({'feature':col,'test':'Mann-Whitney U','status':'not_testable',
                         'statistic':len(left)*len(stayed)/2,'p_value':np.nan,
                         'effect_name':'Rank-biserial (positive = leavers higher)','effect':0.0,
                         'assumption_note':'All values are equal; rank variance is zero, so no inferential p-value is reported.'})
            continue
        statistic, p = mannwhitneyu(left, stayed, alternative='two-sided', method='asymptotic')
        rows.append({'feature':col, 'test':'Mann-Whitney U', 'status':'ok', 'statistic':statistic, 'p_value':p,
                     'effect_name':'Rank-biserial (positive = leavers higher)',
                     'effect':2*statistic/(len(left)*len(stayed))-1,
                     'assumption_note':'Distribution comparison; median interpretation requires similar distribution shapes'})
    result = pd.DataFrame(rows)
    result['p_holm'] = np.nan
    valid = result.status == 'ok'
    result.loc[valid,'p_holm'] = holm(result.loc[valid,'p_value'])
    return result
