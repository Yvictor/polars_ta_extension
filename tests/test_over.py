"""Ordinary Polars windows must match independent partition-local evaluation."""
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import polars as pl
import polars_talib as ta
import pytest
from polars.testing import assert_frame_equal
from test_complete_api import API, column, frame


def grouped_frame(layout):
    data=pl.concat([frame(n).with_columns(pl.lit(g).cast(pl.Int32).alias('symbol'),
                                        pl.int_range(pl.len()).alias('row'))
                    for g,n in enumerate([1,2,19,70,130])])
    data=data.with_columns(pl.when(pl.col('row').is_in([0,35])).then(None).otherwise(pl.col('close')).alias('close'),
                           pl.when(pl.col('symbol')==1).then(None).otherwise(pl.col('symbol')).alias('symbol'),
                           (pl.col('row')%2).alias('session'))
    if layout=='interleaved': data=data.sort('row','symbol')
    if layout=='empty': data=data.head(0)
    return data.with_row_index('_index')


def partition_reference(data, expression, keys):
    """Host group selection is independent of the window execution path."""
    if data.is_empty():
        return data.select(expression.alias('r'))
    pieces = [part.select('_index', expression.alias('r'))
              for part in data.partition_by(keys, maintain_order=True)]
    return pl.concat(pieces).sort('_index').select('r')


@pytest.mark.parametrize('spec',API,ids=lambda f:f['name'])
@pytest.mark.parametrize('layout',['contiguous','interleaved','empty'])
def test_all_indicators_over_match_independent_partitions(spec,layout):
    data=grouped_frame(layout)
    args=[pl.col(column(i)) for i in spec['inputs']]
    keys=['symbol','session']
    direct=data.lazy().select(getattr(ta,spec['name'])(*args).over(keys).alias('r')).collect()
    expected=partition_reference(data,getattr(ta,spec['name'])(*args),keys)
    # Same kernel, masks, warmups and local indices: exact equality is expected.
    assert_frame_equal(direct,expected,check_exact=True)


@pytest.mark.parametrize('spec',[f for f in API if any(p['name']=='timeperiod' for p in f['params'])],ids=lambda f:f['name'])
@pytest.mark.parametrize('period',[2,5,31])
def test_parameters_and_broadcast_literals(spec,period):
    data=grouped_frame('interleaved')
    args=[pl.col(column(i)) for i in spec['inputs']]
    if len(args)>1: args[-1]=pl.lit(10.)
    direct=data.select(getattr(ta,spec['name'])(*args,timeperiod=period).over('symbol').alias('r'))
    expected=partition_reference(data,getattr(ta,spec['name'])(*args,timeperiod=period),['symbol'])
    assert_frame_equal(direct,expected,check_exact=True)


def test_original_api_and_grouped_errors():
    assert not hasattr(ta, 'by_group')
    data=grouped_frame('contiguous')
    with pytest.raises(pl.exceptions.ComputeError):
        data.select(ta.rsi(timeperiod=-1).over('symbol'))


def test_concurrent_calls_and_lifecycle_are_independent():
    from polars_talib._polars_talib import initialize,shutdown
    data=grouped_frame('interleaved')
    def compute(i):
        initialize();shutdown()
        return data.select(ta.macd().over('symbol').alias('m'),ta.atr().over('symbol').alias('a'))
    reference=compute(0)
    with ThreadPoolExecutor(max_workers=4) as pool:
        for got in pool.map(compute,range(24)):assert_frame_equal(got,reference,check_exact=True)


@pytest.mark.parametrize('dtype',[pl.String,pl.Float64,pl.Boolean,pl.Categorical,pl.Date])
def test_group_key_dtypes_match_polars(dtype):
    keys=pl.Series('key',np.arange(60)%3)
    if dtype==pl.Categorical:keys=keys.cast(pl.String)
    data=frame(60).with_columns(keys.cast(dtype)).with_row_index('_index')
    if dtype==pl.Float64:
        data=data.with_columns(pl.when(pl.int_range(pl.len())%7==0).then(float('nan')).otherwise(pl.col('key')).alias('key'))
    data=data.with_columns(pl.when(pl.int_range(pl.len())%11==0).then(None).otherwise(pl.col('key')).alias('key'))
    assert_frame_equal(data.select(ta.macd().over('key').alias('r')),
                       partition_reference(data,ta.macd(),['key']),check_exact=True)


def test_expression_keys_with_duplicate_source_names():
    from datetime import date
    data=pl.DataFrame({'date':[date(2026,1,1),date(2026,1,2),date(2026,2,1),date(2026,2,2)],'close':[1.,2.,3.,4.]}).with_row_index('_index')
    keys=[pl.col('date').dt.year(),pl.col('date').dt.month()]
    expected=partition_reference(data.with_columns(keys[0].alias('year'),keys[1].alias('month')),ta.sma(timeperiod=2),['year','month'])
    assert_frame_equal(data.select(ta.sma(timeperiod=2).over(keys).alias('r')),expected,check_exact=True)


@pytest.mark.parametrize('keys',[
    pl.Series('key',[[i%3,i%2] for i in range(60)]),
    pl.Series('key',[[i%3,i%2] for i in range(60)],dtype=pl.Array(pl.Int64,2)),
    pl.Series('key',[{'x':i%3,'y':None if i%2 else i%2} for i in range(60)]),
    pl.Series('key',[bytes([i%3]) for i in range(60)]),
    pl.Series('key',[None]*60,dtype=pl.Null),
])
def test_nested_binary_and_null_keys_use_host_window_grouping(keys):
    data=frame(60).with_columns(keys).with_row_index('_index')
    # Polars 1.20 cannot group FixedSizeList directly; its List conversion has
    # identical key equality and provides the independent window reference.
    reference_key = pl.col('key').arr.to_list() if isinstance(keys.dtype,pl.Array) else pl.col('key')
    normalized=data.with_columns(reference_key.alias('key'))
    assert_frame_equal(data.select(ta.rsi(timeperiod=2).over(reference_key).alias('r')),
                       partition_reference(normalized,ta.rsi(timeperiod=2),['key']),check_exact=True)
