"""Optional reproducible held-out comparison; fit preprocessing on training only."""
import pandas as pd
import warnings
from sklearn.exceptions import ConvergenceWarning
from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from .data import RAW_COLUMNS, validate_prepared

EXCLUDED = {'Attrition','EmployeeNumber','EmployeeCount','Over18','StandardHours'}


def build_pipeline():
    """All fitted transformations live inside the training pipeline."""
    preprocessor = ColumnTransformer([
        ('numeric', make_pipeline(SimpleImputer(strategy='median'), StandardScaler()), make_column_selector(dtype_include='number')),
        ('category', make_pipeline(SimpleImputer(strategy='most_frequent'), OneHotEncoder(handle_unknown='ignore')), make_column_selector(dtype_exclude='number'))])
    return make_pipeline(preprocessor, LogisticRegression(class_weight='balanced', max_iter=3000, random_state=42))


def split_model_data(df):
    validate_prepared(df)
    X = df[[c for c in df if c in RAW_COLUMNS-EXCLUDED]].copy()
    y = df.AttritionFlag.copy()
    if set(y.unique()) != {0,1}:
        raise ValueError('Model evaluation requires both attrition classes.')
    if y.value_counts().min() < 2 or len(df) < 5:
        raise ValueError('Model evaluation needs enough observations of both classes for a stratified 80/20 split.')
    if X.empty:
        raise ValueError('No supported model predictors are available.')
    parts = train_test_split(X, y, test_size=.2, stratify=y, random_state=42)
    if any(set(part.unique()) != {0,1} for part in parts[2:]):
        raise ValueError('The stratified split needs both classes in training and holdout; add more minority observations.')
    return parts

def evaluate_models(df):
    Xtrain, Xtest, ytrain, ytest = split_model_data(df)
    models = {'majority_baseline':DummyClassifier(strategy='most_frequent'),
              'logistic_regression':build_pipeline()}
    rows = []
    for name, model in models.items():
        with warnings.catch_warnings():
            warnings.simplefilter('error', ConvergenceWarning)
            try:
                model.fit(Xtrain, ytrain)
            except ConvergenceWarning as exc:
                raise ValueError('Logistic regression did not converge; inspect inputs before reporting metrics.') from exc
        pred = model.predict(Xtest)
        prob = model.predict_proba(Xtest)[:, 1]
        tn, fp, fn, tp = confusion_matrix(ytest, pred, labels=[0,1]).ravel()
        rows.append({'model':name, 'train_n':len(ytrain), 'test_n':len(ytest),
                     'accuracy':accuracy_score(ytest,pred), 'precision':precision_score(ytest,pred,zero_division=0),
                     'recall':recall_score(ytest,pred,zero_division=0), 'f1':f1_score(ytest,pred,zero_division=0),
                     'roc_auc':roc_auc_score(ytest,prob), 'tn':int(tn),'fp':int(fp),'fn':int(fn),'tp':int(tp)})
    return pd.DataFrame(rows)
