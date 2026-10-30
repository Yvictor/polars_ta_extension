"""Untimed public CMOU differential capture for the checked-window candidate."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import polars as pl
import polars_talib as ta


def inputs(kind,n):
    x=100.+np.sin(np.arange(n,dtype=float)*.71)
    if kind=='flat':x[:]=3.3
    elif kind=='minus_zero':x[:]=-0.
    elif kind=='alternating_zero':x=np.where(np.arange(n)%2,0.,-0.)
    elif kind=='flat_then_move':x[:n//2]=1.
    elif kind=='move_then_flat':x[n//2:]=1.
    elif kind=='tiny':x*=1e-310
    elif kind=='high_offset':x=1e12+(np.arange(n)%7)*.25
    elif kind=='huge':x=np.where(np.arange(n)%2,-1e308,1e308)
    elif kind=='all_nan':x[:]=np.nan
    elif n and kind=='leading_nan':x[:min(n,3)]=np.nan
    elif n and kind=='nan':x[n//2]=np.nan
    elif n and kind=='positive_inf':x[n//2]=np.inf
    elif n and kind=='negative_inf':x[n//2]=-np.inf
    values=x.tolist()
    if kind=='all_null':values=[None]*n
    elif n and kind=='null':values[n//2]=None
    elif kind=='leading_null':values[:min(n,3)]=[None]*min(n,3)
    return values


def cases():
    kinds=('finite','flat','minus_zero','alternating_zero','flat_then_move','move_then_flat','tiny','high_offset','huge','all_nan','leading_nan','nan','positive_inf','negative_inf','all_null','null','leading_null')
    for n in(0,1,2,13,14,15,31,64):
        for kind in kinds:
            frame=pl.DataFrame({'close':pl.Series('close',inputs(kind,n),dtype=pl.Float64)})
            for period in(None,2,3,14,30,128,100000,0,1,-1):
                yield f'direct/{kind}/{n}/p{period}',frame,period,'name',False,False
    for groups,bars in((4,100),(8,17),(32,4)):
        n=groups*bars
        for kind in('finite','null','nan','alternating_zero'):
            base=pl.DataFrame({'close':pl.Series('close',inputs(kind,n),dtype=pl.Float64),'g':np.repeat(np.arange(groups),bars)})
            for interleaved in(False,True):
                frame=base[np.arange(n).reshape(groups,bars).T.ravel()]if interleaved else base
                for period in(2,14,30,128):
                    for form in('name','expr','namespace'):
                        for lazy in(False,True):
                            key=f'over/{kind}/{groups}x{bars}/inter{interleaved}/p{period}/{form}/lazy{lazy}'
                            yield key,frame,period,form,lazy,True
    for kind in('finite','null','nan','alternating_zero'):
        base=pl.DataFrame({'close':pl.Series('close',inputs(kind,64),dtype=pl.Float64)})
        chunked=pl.concat([base[:17],base[17:35],base[35:]],rechunk=False)
        for frame,label in((chunked,'chunked'),(base.with_columns(pl.col('close').cast(pl.Float32)),'float32')):
            for form in('name','expr','namespace'):
                for lazy in(False,True):yield f'{label}/{kind}/{form}/lazy{lazy}',frame,3,form,lazy,False


def expression(period,form,grouped):
    kwargs={}if period is None else{'timeperiod':period}
    result=pl.col('close').ta.cmou(**kwargs)if form=='namespace'else ta.cmou('close'if form=='name'else pl.col('close'),**kwargs)
    return (result.over('g')if grouped else result).alias('result')


def capture(path):
    metadata={'cases':{},'input_sha256':{},'polars':pl.__version__,'numpy':np.__version__,'talib':ta.__talib_version__};arrays={}
    for i,(name,frame,period,form,lazy,grouped)in enumerate(cases()):
        assert name not in metadata['cases'], 'duplicate public case'
        digest=hashlib.sha256(str(frame.schema).encode())
        for column in frame:
            digest.update(column.name.encode());digest.update(column.fill_null(0).to_numpy().tobytes());digest.update(column.is_null().to_numpy().tobytes())
        metadata['input_sha256'][name]=digest.hexdigest()
        try:
            expr=expression(period,form,grouped);result=frame.lazy().select(expr).collect()if lazy else frame.select(expr)
        except Exception as exc:
            metadata['cases'][name]={'error':type(exc).__name__};continue
        assert result.width==1 and result.height==frame.height and result.to_series().dtype==pl.Float64
        key='value_'+str(i);column=result.to_series();arrays[key]=column.fill_null(0).to_numpy();arrays[key+'_null']=column.is_null().to_numpy();metadata['cases'][name]={'schema':str(result.schema),'key':key,'rows':result.height}
    assert len(metadata['cases'])==1984 and sum('error'in row for row in metadata['cases'].values())==408, 'unexpected public success/error inventory'
    module=next(Path(ta.__file__).parent.glob('_polars_talib*.so'));metadata['native_sha256']=hashlib.sha256(module.read_bytes()).hexdigest();arrays['metadata']=np.array(json.dumps(metadata));np.savez_compressed(path,**arrays)
    print(json.dumps({'cases':len(metadata['cases']),'errors':sum('error'in v for v in metadata['cases'].values()),'output_values':sum(v['rows']for v in metadata['cases'].values()if'error'not in v),'talib':metadata['talib']}))


def compare(before,after,exact=False):
    with np.load(before,allow_pickle=False)as a,np.load(after,allow_pickle=False)as b:
        am=json.loads(str(a['metadata']));bm=json.loads(str(b['metadata']));assert set(am['cases'])==set(bm['cases'])and len(am['cases'])==1984;assert am['input_sha256']==bm['input_sha256'];assert am['polars']==bm['polars']and am['numpy']==bm['numpy'];checked=0;maximum=0.
        for name,old in am['cases'].items():
            new=bm['cases'][name]
            if 'error'in old or'error'in new:assert old==new,(name,old,new);continue
            assert old['schema']==new['schema']and old['rows']==new['rows'],name;x=a[old['key']];y=b[new['key']];xn=a[old['key']+'_null'];yn=b[new['key']+'_null'];assert x.dtype==y.dtype and x.shape==y.shape,name
            np.testing.assert_array_equal(xn,yn,err_msg=name)
            for predicate in(np.isnan,np.isposinf,np.isneginf):np.testing.assert_array_equal(predicate(x),predicate(y),err_msg=name)
            both_zero=(x==0)&(y==0);np.testing.assert_array_equal(np.signbit(x[both_zero]),np.signbit(y[both_zero]),err_msg=name)
            if exact:
                valid=~np.isnan(x);np.testing.assert_array_equal(x[valid].view('u8'),y[valid].view('u8'),err_msg=name)
            else:np.testing.assert_allclose(x,y,rtol=1e-10,atol=1e-10,equal_nan=True,err_msg=name)
            valid=np.isfinite(x)&np.isfinite(y)
            if valid.any():maximum=max(maximum,float(np.max(np.abs(x[valid]-y[valid]))))
            checked+=len(x)
    return {'cases':len(am['cases']),'checked_values':checked,'exact':exact,'max_absolute_difference':maximum,'zero_sign_policy':'both-zero exact','nan_payload_policy':'positions exact; NaN sign/payload excluded'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--capture',type=Path);p.add_argument('--compare',nargs=2,type=Path);p.add_argument('--exact',action='store_true');a=p.parse_args()
    if a.capture:capture(a.capture)
    else:print(json.dumps(compare(*a.compare,exact=a.exact)))
