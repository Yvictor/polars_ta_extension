"""Fixed case shapes/output ranges; no runtime/product imports."""
FUNCTIONS=('ema','rsi','macd','atr','adx','cci','stddev','ppo')
LOOKBACKS={'cmou':14,'ppo':25,'ema':29,'mavp':29,'atr':14,'correl':29,
           'add':0,'cdlengulfing':2,'sarext':1,'mavp_one':29,
           'rsi':14,'macd':33,'adx':27,'cci':13,'stddev':4}
def contract(name):
    family,layout=name.split('/')
    grouped=family.startswith('grouped_')or family=='control_cumsum'
    interleaved=layout.endswith('_interleaved');shape=layout.removesuffix('_interleaved')
    groups,bars=map(int,shape.split('x'))if grouped else(1,int(shape))
    rows=groups*bars;kind=family.removeprefix('grouped_')
    if family.startswith('control_cumsum'):functions=()
    else:functions=FUNCTIONS if kind=='mix8'else(kind,)
    lookbacks=[];dtypes=[]
    for f in functions:
        for _ in range(3 if f=='macd'else 1):
            lookbacks.append(LOOKBACKS[f]);dtypes.append('Int32'if f=='cdlengulfing'else'Float64')
    if not functions:lookbacks=[0];dtypes=['Float64']
    return {'case':name,'family':kind,'rows':rows,'groups':groups,'bars':bars,'grouped':grouped,
            'interleaved':interleaved,'functions':list(functions),'output_fields':len(lookbacks),
            'lookbacks':lookbacks,'dtypes':dtypes,
            'written_values':[groups*max(0,bars-lb)for lb in lookbacks],
            'uniform_period14':kind=='mavp_one','all_inputs_finite':True}
