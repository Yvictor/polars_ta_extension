"""Untimed public C-target short-zero regression; never a performance waiver."""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
import polars as pl
import polars_talib as ta
from sarext_typed_provenance import identity,source_record

FIXTURES=(
    ('short_zero',[0.,-1.,-2.],[-1.,-2.,-3.],{},1),
    ('short_cancellation',[-1.,-1.,-1.,-1.],[-2.,-2.,-2.,-2.],
     {'startvalue':-2.,'accelerationinitshort':.5,'accelerationshort':0.,'accelerationmaxshort':.5},2),
)


def capture(source,pin):
    rows={}
    for name,high,low,params,changed in FIXTURES:
        for grouped in (False,True):
            count=3 if grouped else 1
            data=pl.concat([pl.DataFrame({'high':high,'low':low,'symbol':[g]*len(high),'within':range(len(high))}) for g in range(count)])
            if grouped:data=data.sort('within','symbol')
            expression=ta.sarext(pl.col('high'),pl.col('low'),**params)
            if grouped:expression=expression.over('symbol')
            eager=data.select(expression.alias('value')).to_series()
            lazy=data.lazy().select(expression.alias('value')).collect().to_series()
            a=eager.fill_null(np.nan).to_numpy();b=lazy.fill_null(np.nan).to_numpy()
            np.testing.assert_array_equal(eager.is_null().to_numpy(),lazy.is_null().to_numpy())
            np.testing.assert_array_equal(a.view(np.uint64),b.view(np.uint64))
            positions=np.flatnonzero(data['within'].to_numpy()==changed).tolist()
            rows[name+('/interleaved' if grouped else '/dense')]={
                'params':params,'schema':str(eager.dtype),'nulls':eager.is_null().to_list(),
                'nan':np.isnan(a).tolist(),'words':[int(x) for x in a.view(np.uint64)],
                'target_zero_positions':positions,'groups':count,
                'high_words':[int(x) for x in data['high'].to_numpy().view(np.uint64)],
                'low_words':[int(x) for x in data['low'].to_numpy().view(np.uint64)],
                'symbol':data['symbol'].to_list(),'within':data['within'].to_list(),
                'eager_lazy_raw_identity':True}
    return {'source':source_record(source,pin),'identity':identity(Path(sys.executable)),
            'cases':rows,'scope':'Untimed explicit C-target boundary. Baseline56 known short-zero sign difference is never accepted in timed queries or the full corpus.'}


def validate(rows):
    if set(rows)!={'original','prior','candidate','alternative'}:raise ValueError('four public regression captures required')
    original=rows['original']['cases'];expected={name+'/'+layout for name,*_ in FIXTURES for layout in ('dense','interleaved')}
    if set(original)!=expected:raise ValueError('C-target regression scope differs')
    result={}
    for name,reference in original.items():
        positions=reference['target_zero_positions']
        if len(positions)!=reference['groups'] or any(reference['words'][i]!=0 for i in positions):raise ValueError('C does not have the documented positive-zero boundary')
        for side in ('prior','candidate','alternative'):
            got=rows[side]['cases']
            if set(got)!=expected:raise ValueError('public regression omitted cases')
            case=got[name]
            for key in reference:
                if key!='words' and case[key]!=reference[key]:raise ValueError('public C-target metadata/masks differ: '+side+'/'+name+'/'+key)
            expected_words=list(reference['words'])
            if side=='prior':
                for index in positions:expected_words[index]=0x8000000000000000
            if case['words']!=expected_words:raise ValueError('C-target short-zero words differ outside the documented boundary: '+side+'/'+name)
        result[name]={'C_target_words':reference['words'],'known56_negative_zero_positions':positions,
                      'A_B_C_raw_identity':True,'timed_waiver':False}
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-root',type=Path,required=True)
    p.add_argument('--expected-commit',required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(capture(args.source_root,args.expected_commit),indent=2)+'\n')
