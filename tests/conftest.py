import pytest
import polars as pl
import numpy as np

np.random.seed(666)


@pytest.fixture
def df_with_close():
    ser = (pl.Series("close", np.random.randint(-10, 12, size=50000)).cast(float) / 10.0).cum_sum()
    return pl.DataFrame(ser)


@pytest.fixture
def df_ohlc():
    ser = (pl.Series("close", np.random.randint(-10, 12, size=50000)).cast(float) / 10.0).cum_sum()
    sers = [
        (ser + (np.random.randint(-5, 5, size=50000) / 10.0)).alias("open"),
        (ser + (np.random.randint(0, 12, size=50000) / 10.0)).alias("high"),
        (ser + (np.random.randint(-10, 0, size=50000) / 10.0)).alias("low"),
        ser,
    ]
    return pl.DataFrame(sers)
