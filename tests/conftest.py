from pathlib import Path
import pandas as pd
import pytest
from src.data import RAW_NAME, prepare

ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture(scope='session')
def raw_path():
    return ROOT/'data/raw'/RAW_NAME

@pytest.fixture
def raw_frame(raw_path):
    return pd.read_csv(raw_path)

@pytest.fixture(scope='session')
def prepared(raw_path):
    return prepare(raw_path)[0]
