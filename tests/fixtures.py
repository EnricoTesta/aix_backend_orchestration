import pytest
from pandas import DataFrame
from datetime import datetime


@pytest.fixture()
def user_id():
    return 'TestUser'

@pytest.fixture
def db_list():
    return ['ID001', '#', 1, 'NULL', datetime(2000, 1, 1, 18, 15)]

@pytest.fixture
def predictions_2models_binary():
    return DataFrame([['2022-01-01', 'AAPL', 0., 1.],
                      ['2022-01-01', 'MSFT', 0., 1.],
                      ['2022-01-01', 'AA', 0., 1.]], columns=['OBS_DATE', 'Ticker', 'Model_1', 'Model_2'])\
        .set_index(['OBS_DATE', 'Ticker'], drop=True)

@pytest.fixture
def target_binary():
    return DataFrame([['2022-01-01', 'AAPL', 1.],
                      ['2022-01-01', 'MSFT', 1.],
                      ['2022-01-01', 'AA', 1.]], columns=['OBS_DATE', 'Ticker', 'TARGET_VARIABLE'])\
        .set_index(['OBS_DATE', 'Ticker'], drop=True)
