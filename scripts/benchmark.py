"""Deterministic end-to-end Polars benchmarks; run in an installed wheel environment."""
import argparse
import gc
import json
import os
import platform
import statistics
import time
from pathlib import Path
import numpy as np
import polars as pl
import polars_talib as ta


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--repeats', type=int, default=15)
    args = parser.parse_args()
    results = {}
    for size in (1_000, 100_000, 1_000_000):
        rng = np.random.default_rng(26)
        close = 100 + rng.normal(0, .1, size).cumsum()
        df = pl.DataFrame({'close': close, 'high': close+1, 'low': close-1,
                           'g': np.arange(size)//1000})
        cases = {
            'ema': (df, [ta.ema()]),
            'rsi': (df, [ta.rsi()]),
            'macd': (df, [ta.macd()]),
            'atr': (df, [ta.atr()]),
            'multi': (df, [ta.ema().alias('ema'), ta.rsi().alias('rsi'), ta.macd().alias('macd'), ta.atr().alias('atr')]),
            'grouped_rsi': (df, [ta.rsi().over('g')]),
            'null_rsi': (df.with_columns(pl.when(pl.int_range(pl.len())%101==0).then(None).otherwise(pl.col('close')).alias('close')), [ta.rsi()]),
            'chunked_ema': (pl.concat([df.slice(i, size//10) for i in range(0,size,size//10)], rechunk=False), [ta.ema()]),
        }
        for name, (data, exprs) in cases.items():
            query = data.lazy().select(exprs)
            for _ in range(3): query.collect()
            samples=[]
            gc.disable()
            try:
                for _ in range(args.repeats):
                    start=time.perf_counter_ns()
                    result=query.collect()
                    elapsed=time.perf_counter_ns()-start
                    assert result.height==size
                    samples.append(elapsed/1e6)
            finally: gc.enable()
            results[f'{name}/{size}']={'median_ms':statistics.median(samples),'min_ms':min(samples),'samples_ms':samples}
    payload={'python':platform.python_version(), 'platform':platform.platform(), 'cpu':platform.processor(),
             'polars':pl.__version__, 'talib':ta.__talib_version__, 'threads':pl.thread_pool_size(),
             'repeats':args.repeats, 'results':results}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps({k:round(v['median_ms'],4) for k,v in results.items()},indent=2))

if __name__=='__main__': main()
