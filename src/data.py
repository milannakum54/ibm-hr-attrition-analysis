"""Load, validate and prepare the fictional IBM HR sample."""
from pathlib import Path
import hashlib
import csv
from io import StringIO
from collections import Counter
import numpy as np
import pandas as pd

RAW_NAME = 'WA_Fn-UseC_-HR-Employee-Attrition.csv'
GROUPS = ['OverTime', 'Department', 'JobRole', 'AgeGroup', 'JobLevel',
          'JobSatisfactionLabel', 'EnvironmentSatisfactionLabel',
          'WorkLifeBalanceLabel', 'BusinessTravel']
NUMERIC = ['Age', 'MonthlyIncome', 'YearsAtCompany', 'DistanceFromHome', 'JobLevel', 'TotalWorkingYears']
NUMERIC_FIELDS = set(NUMERIC) | {
    'DailyRate','Education','EmployeeCount','EmployeeNumber','EnvironmentSatisfaction',
    'HourlyRate','JobInvolvement','JobSatisfaction','MonthlyRate','NumCompaniesWorked',
    'PercentSalaryHike','PerformanceRating','RelationshipSatisfaction','StandardHours',
    'StockOptionLevel','TrainingTimesLastYear','WorkLifeBalance','YearsInCurrentRole',
    'YearsSinceLastPromotion','YearsWithCurrManager'}
CATEGORY_VALUES = {
    'Attrition': {'Yes','No'}, 'OverTime': {'Yes','No'},
    'BusinessTravel': {'Non-Travel','Travel_Rarely','Travel_Frequently'},
    'Department': {'Sales','Research & Development','Human Resources'},
    'JobRole': {'Sales Executive','Research Scientist','Laboratory Technician',
                'Manufacturing Director','Healthcare Representative','Manager',
                'Sales Representative','Research Director','Human Resources'},
    'EducationField': {'Life Sciences','Medical','Marketing','Technical Degree','Human Resources','Other'},
    'Gender': {'Male','Female'}, 'MaritalStatus': {'Single','Married','Divorced'}, 'Over18': {'Y'}}
RAW_COLUMNS = NUMERIC_FIELDS | set(CATEGORY_VALUES)
REQUIRED = {'Attrition', 'EmployeeNumber', 'OverTime', 'Department', 'JobRole',
            'JobSatisfaction', 'EnvironmentSatisfaction', 'WorkLifeBalance',
            'BusinessTravel', *NUMERIC}

def validate_values(frame):
    """Validate present source fields before dropping anything, including constants."""
    for col in ['Department', 'JobRole', 'BusinessTravel']:
        if col in frame and not frame[col].map(lambda v: isinstance(v,str) and bool(v.strip())).all():
            raise ValueError(f'{col} must contain nonblank category labels.')
    for col, allowed in CATEGORY_VALUES.items():
        if col in frame and not frame[col].isin(allowed).all():
            if col in ['Attrition','OverTime']:
                raise ValueError(f'{col} must contain only Yes and No.')
            raise ValueError(f'{col} contains unsupported category values: {sorted(allowed)} expected.')
    for col in sorted(NUMERIC_FIELDS & set(frame.columns)):
        if (not pd.api.types.is_numeric_dtype(frame[col]) or pd.api.types.is_bool_dtype(frame[col])
                or not np.isfinite(frame[col]).all()):
            raise ValueError(f'{col} must contain finite numeric values.')
        if (frame[col] < 0).any():
            raise ValueError(f'{col} cannot be negative.')
        if (frame[col] > 1e12).any():
            raise ValueError(f'{col} exceeds the supported numeric bound of 1e12.')
        # Rate/income fields may be fractional; counts, years, IDs and ratings are integers.
        if col not in {'MonthlyIncome','DailyRate','HourlyRate','MonthlyRate'} and not (frame[col] % 1 == 0).all():
            raise ValueError(f'{col} must contain whole years or integer codes/counts.')
    if 'Age' in frame and not frame.Age.between(18,100).all():
        raise ValueError('Age must be between 18 and 100 for this project.')
    if 'JobLevel' in frame and not frame.JobLevel.isin(range(1,6)).all():
        raise ValueError('JobLevel must use levels 1 to 5.')
    ratings = ['EnvironmentSatisfaction','JobSatisfaction','WorkLifeBalance',
               'JobInvolvement','RelationshipSatisfaction','PerformanceRating']
    for col in ratings:
        if col in frame and not frame[col].isin([1,2,3,4]).all():
            raise ValueError(f'{col} must use ratings 1 to 4.')
    for col, allowed in {'Education':range(1,6),'StockOptionLevel':range(4),
                         'EmployeeCount':[1],'StandardHours':[80]}.items():
        if col in frame and not frame[col].isin(allowed).all():
            raise ValueError(f'{col} contains unsupported codes/values.')


def validate_prepared(df, columns=()):
    """Check analysis inputs rather than trusting manually edited prepared frames."""
    if df.empty:
        raise ValueError('The dataset is empty.')
    if not df.columns.is_unique:
        raise ValueError('Duplicate column names are not supported.')
    needed = set(columns) | {'Attrition','AttritionFlag'}
    missing = needed-set(df.columns)
    if missing:
        raise ValueError(f'Missing required analysis columns: {sorted(missing)}')
    if df[list(needed)].isna().any().any():
        raise ValueError('Missing values in analysis columns.')
    validate_values(df)
    if not df.AttritionFlag.isin([0,1]).all():
        raise ValueError('AttritionFlag must contain only 0 and 1.')
    if not (df.Attrition.map({'No':0,'Yes':1}) == df.AttritionFlag).all():
        raise ValueError('Attrition and AttritionFlag disagree.')


def prepare(path):
    """Return validated data and an audit without changing the input file."""
    path = Path(path)
    source = path.read_bytes()
    try:
        text = source.decode('utf-8-sig')
        if '\x00' in text:
            raise ValueError('CSV contains a NUL byte; repair the source file before analysis.')
        rows = [row for row in csv.reader(StringIO(text), strict=True) if row]
    except (UnicodeDecodeError, csv.Error) as exc:
        raise ValueError(f'Expected a valid UTF-8 CSV: {exc}') from exc
    if not rows:
        raise ValueError('The dataset is empty.')
    duplicates = [c for c,n in Counter(rows[0]).items() if n > 1]
    if duplicates:
        raise ValueError(f'Duplicate CSV column names: {duplicates}')
    for number,row in enumerate(rows[1:],start=2):
        if len(row) != len(rows[0]):
            raise ValueError(f'CSV record {number} has {len(row)} fields; expected {len(rows[0])}.')
    raw = pd.read_csv(StringIO(text), skip_blank_lines=True)
    unknown = set(raw.columns)-RAW_COLUMNS
    if unknown:
        raise ValueError(f'Unexpected columns outside the IBM HR input schema: {sorted(unknown)}')
    missing = REQUIRED - set(raw.columns)
    if missing:
        raise ValueError(f'Missing required columns: {sorted(missing)}')
    if raw.empty:
        raise ValueError('The dataset is empty.')
    if raw.isna().any().any():
        raise ValueError('Missing values found. Inspect them before choosing an imputation policy.')
    validate_values(raw)
    clean = raw.drop_duplicates().copy()
    if clean.EmployeeNumber.duplicated().any():
        raise ValueError('Conflicting records share EmployeeNumber; resolve them explicitly.')
    constants = [c for c in clean if clean[c].nunique() == 1]
    # A filtered sample can have one department or one target class. Keep
    # required fields so callers can still compute descriptive summaries.
    retained_constants = [c for c in constants if c in REQUIRED and c != 'EmployeeNumber']
    # Only fixed metadata constants are removed. Predictor selection is not
    # learned from the full dataset before the model's train/holdout split.
    dropped = [c for c in constants if c in {'EmployeeCount','StandardHours','Over18'}] + ['EmployeeNumber']
    clean = clean.drop(columns=dropped)
    clean['AttritionFlag'] = clean.Attrition.map({'No': 0, 'Yes': 1})
    clean['AgeGroup'] = pd.cut(clean.Age, [17, 29, 39, 49, 100],
                               labels=['18-29', '30-39', '40-49', '50+'])
    for col in ['JobSatisfaction', 'EnvironmentSatisfaction']:
        clean[col + 'Label'] = clean[col].map({1:'1 Low', 2:'2 Medium', 3:'3 High', 4:'4 Very high'})
    clean['WorkLifeBalanceLabel'] = clean.WorkLifeBalance.map(
        {1:'1 Bad', 2:'2 Good', 3:'3 Better', 4:'4 Best'})
    rate_cols = [c for c in ['DailyRate', 'HourlyRate', 'MonthlyRate'] if c in clean]
    for col in rate_cols:
        if not pd.api.types.is_numeric_dtype(clean[col]) or not np.isfinite(clean[col]).all():
            raise ValueError(f'{col} must contain finite numeric values.')
    rate_income = {
        c: float(clean[c].corr(clean.MonthlyIncome, method='spearman'))
        if clean[c].nunique() > 1 and clean.MonthlyIncome.nunique() > 1 else None
        for c in rate_cols
    }
    # Preserve these columns; weak income correlation alone does not establish irrelevance.
    report = {'raw_rows': len(raw), 'raw_columns': len(raw.columns),
              'clean_rows': len(clean), 'duplicates_removed': len(raw)-len(clean),
              'missing_cells': int(raw.isna().sum().sum()), 'dropped_columns': dropped,
              'retained_required_constants': retained_constants,
              'retained_predictor_constants': [c for c in constants if c not in dropped],
              'clean_columns': len(clean.columns),
              'validation_policy': 'Reject missing/invalid values; remove exact duplicates; reject conflicting IDs.',
              'rate_income_spearman': rate_income,
              'rate_column_decision': 'Retained; correlation alone is insufficient grounds for removal.',
              'sha256': hashlib.sha256(source).hexdigest()}
    return clean, report

def group_rates(df, column):
    """Within-group rate: leavers / employees in that group, never total rows."""
    if df.empty:
        raise ValueError('Cannot calculate rates for an empty dataset.')
    if not df.columns.is_unique:
        raise ValueError('Duplicate column names are not supported.')
    if column in {'n','left','rate_pct','small_group','AttritionFlag'}:
        raise ValueError(f'{column} is a reserved rate-table name.')
    missing = {column, 'AttritionFlag'} - set(df.columns)
    if missing:
        raise ValueError(f'Missing rate-table columns: {sorted(missing)}')
    if df[[column, 'AttritionFlag']].isna().any().any():
        raise ValueError('Rate-table groups and targets must not be missing.')
    if df[column].map(lambda value: isinstance(value,str) and not value.strip()).any():
        raise ValueError('Rate-table groups must not be blank.')
    if not df.AttritionFlag.isin([0, 1]).all():
        raise ValueError('AttritionFlag must contain only 0 and 1.')
    result = df.groupby(column, observed=True).AttritionFlag.agg(n='size', left='sum')
    result['rate_pct'] = result.left / result.n * 100
    result['small_group'] = result.n < 30
    return result.reset_index()
