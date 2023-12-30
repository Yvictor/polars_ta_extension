import pytest
import polars as pl
import numpy as np

np.random.seed(666)


@pytest.fixture
def df_with_close():
    ser = (pl.Series("close", np.random.randint(-10, 12, size=100000)).cast(float) / 10.0).cum_sum()
    return pl.DataFrame(ser)
