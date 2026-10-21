"""Malformed-file and complete schema validation matrix."""
import json
import numpy as np
import pandas as pd
import pytest
from src.data import prepare, REQUIRED, NUMERIC_FIELDS, CATEGORY_VALUES

def write(tmp_path,frame):
    path=tmp_path/'input.csv'; frame.to_csv(path,index=False); return path

@pytest.mark.parametrize('column', sorted(REQUIRED))
def test_each_required_column_missing(raw_frame,tmp_path,column):
    with pytest.raises(ValueError,match='Missing required columns'):
        prepare(write(tmp_path,raw_frame.head(10).drop(columns=column)))

@pytest.mark.parametrize('column', sorted(NUMERIC_FIELDS))
@pytest.mark.parametrize('value', [-1,np.inf])
def test_numeric_constraints_every_field(raw_frame,tmp_path,column,value):
    frame=raw_frame.head(10).astype({column:float})
    frame.loc[frame.index[0],column]=value
    with pytest.raises(ValueError,match=column):
        prepare(write(tmp_path,frame))

@pytest.mark.parametrize('column', sorted(CATEGORY_VALUES))
def test_unknown_source_categories(raw_frame,tmp_path,column):
    frame=raw_frame.head(10).copy(); frame.loc[0,column]='unknown'
    with pytest.raises(ValueError,match=column):
        prepare(write(tmp_path,frame))

@pytest.mark.parametrize('column', ['Age','Attrition','EmployeeNumber','JobRole','MonthlyIncome'])
def test_missing_cells_rejected(raw_frame,tmp_path,column):
    frame=raw_frame.head(10).copy()
    if pd.api.types.is_numeric_dtype(frame[column]): frame[column]=frame[column].astype(float)
    frame.loc[0,column]=None
    with pytest.raises(ValueError,match='Missing values'):
        prepare(write(tmp_path,frame))

@pytest.mark.parametrize('contents', [b'',b'\xef\xbb\xbf',b'\xff\xfe\x00\x81',b'Age,Attrition\n"unterminated,Yes',b'Age\x00,Attrition\n18,Yes'])
def test_empty_corrupt_and_invalid_encoding(tmp_path,contents):
    path=tmp_path/'bad.csv'; path.write_bytes(contents)
    with pytest.raises(ValueError): prepare(path)

def test_header_only(raw_frame,tmp_path):
    with pytest.raises(ValueError,match='empty'): prepare(write(tmp_path,raw_frame.head(0)))

def test_missing_file_and_directory(tmp_path):
    with pytest.raises(FileNotFoundError): prepare(tmp_path/'missing.csv')
    with pytest.raises(OSError): prepare(tmp_path)

@pytest.mark.parametrize('column', ['AttritionFlag','AgeGroup','FutureDeparture','Unnamed: 0'])
def test_unexpected_columns_cannot_leak_into_model(raw_frame,tmp_path,column):
    frame=raw_frame.head(10).copy(); frame[column]=1
    with pytest.raises(ValueError,match='Unexpected columns'): prepare(write(tmp_path,frame))

@pytest.mark.parametrize('encoding', ['utf-8','utf-8-sig'])
def test_valid_encoding_blank_lines_reordered_columns(raw_frame,tmp_path,encoding):
    frame=raw_frame.head(20)[list(reversed(raw_frame.columns))]
    path=tmp_path/'data with spaces.csv'
    path.write_text('\n'+frame.to_csv(index=False)+'\n',encoding=encoding)
    clean,audit=prepare(path)
    assert len(clean)==20
    assert clean.AttritionFlag.sum()==frame.Attrition.eq('Yes').sum()
    json.dumps(audit,allow_nan=False)

@pytest.mark.parametrize('age', [17,101,18.5])
def test_age_invalid_boundaries(raw_frame,tmp_path,age):
    frame=raw_frame.head(10).astype({'Age':float}); frame.loc[0,'Age']=age
    with pytest.raises(ValueError,match='Age'): prepare(write(tmp_path,frame))

def test_extreme_value_rejected_without_overflow(raw_frame,tmp_path):
    frame=raw_frame.head(10).astype({'MonthlyIncome':float}); frame.loc[0,'MonthlyIncome']=1e300
    with pytest.raises(ValueError,match='supported numeric bound'): prepare(write(tmp_path,frame))

def test_minimal_supported_schema_retains_required_constants(raw_frame,tmp_path):
    frame=raw_frame.head(1)[sorted(REQUIRED)]
    clean,audit=prepare(write(tmp_path,frame))
    assert len(clean)==1
    assert 'TotalWorkingYears' in clean
    json.dumps(audit,allow_nan=False)
