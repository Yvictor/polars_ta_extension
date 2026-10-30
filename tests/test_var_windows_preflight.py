"""Negative source/static protocol checks; no kernel timing or product import."""
import copy
import importlib.util
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
sys.path.insert(0,str(ROOT/'scripts'))
P = load('var_windows_preflight')
C = load('var_windows_contract')
T = load('var_windows_timed')


class Protocol(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads(P.SPEC.read_text())
        self.temp = tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.base = Path(self.temp.name)

    def fake_spec(self, value):
        return patch.object(P, 'read_json', return_value=value)

    def test_exact_scope_and_p5_alignment(self):
        self.assertEqual(len(P.specification()['cases']), 16)
        self.assertEqual(sum(c['api'] == 'abstract' for c in self.spec['cases']), 2)
        self.assertEqual({c['period'] for c in self.spec['cases'] if c['function'] in ('var','stddev')}, {2,5,200})

    def test_unknown_p14_or_extra_case_rejected(self):
        for mutate in (lambda s:s['cases'].append(copy.deepcopy(s['cases'][0])),
                       lambda s:s['cases'][0].update(period=14),
                       lambda s:s['cases'][0].update(api='newbatch'),
                       lambda s:s.update(samples=30),lambda s:s.update(children_per_profile=575)):
            value = copy.deepcopy(self.spec);mutate(value)
            with self.fake_spec(value),self.assertRaises(ValueError):P.specification()

    def test_unset_and_duplicate_pins_rejected(self):
        unset=copy.deepcopy(self.spec);unset['candidate_commit']='UNSET'
        with self.assertRaises(ValueError):P.pins(unset)
        value = copy.deepcopy(self.spec);value['baseline_current_dev_commit'] = 'a'*40;value['candidate_commit'] = 'a'*40
        with self.assertRaises(ValueError):P.pins(value)
        value['candidate_commit'] = 'b'*40
        self.assertEqual(set(P.pins(value)), set(P.ARMS))
        for bad in ('x'*40, True, 'a'*39, 'a'*40+'\n'):
            value['candidate_commit'] = bad
            with self.assertRaises(ValueError):P.pins(value)

    def test_duplicate_and_nonfinite_json_rejected(self):
        for raw in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'):
            with self.assertRaises(ValueError):P.read_json(raw)

    def test_physical_dyadic_fixture(self):
        p=self.base/'input';record=P.fixture(p,100,'wave');raw=p.read_bytes()
        self.assertEqual(raw[:16],b'VARFIX01'+struct.pack('<Q',100));self.assertEqual(len(raw),1616)
        x=struct.unpack('<100d',raw[16:816]);y=struct.unpack('<100d',raw[816:])
        self.assertEqual(x,tuple(64+((i%37)-18)*.125 for i in range(100)))
        self.assertEqual(y,tuple(32+((i%11)-5)*.0625 for i in range(100)))
        self.assertEqual(record['sha256'],P.sha(p))
        for n,pattern in ((True,'wave'),(1,'wave'),(100,'unknown')):
            with self.assertRaises(ValueError):P.fixture(p,n,pattern)

    def test_flat_and_highoffset_bits(self):
        for pattern in ('flat','highoffset'):
            p=self.base/pattern;P.fixture(p,100,pattern);x=struct.unpack('<100d',p.read_bytes()[16:816])
            expected=tuple(3.3 if pattern=='flat' else 2**40+((i%37)-18)*.125 for i in range(100))
            self.assertEqual(x,expected)

    def valid_capture(self):
        c=next(c for c in self.spec['cases'] if c['rows']==100)
        count=96;raw=b'VAROUT01'+struct.pack('<QQQ',100,4,count)+struct.pack('<d',.125)*count+struct.pack('<Q',P.POISON)*12
        return c,raw

    def test_capture_all_metadata_tails_and_nonfinite(self):
        c,raw=self.valid_capture();p=self.base/'out';p.write_bytes(raw);self.assertEqual(P.capture(p,c),raw)
        mutations=[raw[:-1],b'WRONG001'+raw[8:],raw[:16]+struct.pack('<Q',3)+raw[24:],raw[:24]+struct.pack('<Q',95)+raw[32:],raw[:-8]+struct.pack('<d',0.0),raw[:32]+struct.pack('<d',float('nan'))+raw[40:]]
        for bad in mutations:
            p.write_bytes(bad)
            with self.assertRaises(ValueError):P.capture(p,c)

    def test_actual_symbol_scope_is_not_proof(self):
        binary=self.base/'product';binary.write_bytes(b'\x7fELFfake')
        symbols='0000000000001000 0000000000000020 T ta_lib::ta_func::var::<impl ta_lib::ta_func::types::Core>::var\n0000000000002000 0000000000000030 T ta_lib::ta_func::stddev::<impl ta_lib::ta_func::types::Core>::stddev\n'
        calls=[]
        def output(argv,**kwargs):
            calls.append(argv)
            return symbols if argv[0]=='nm' else '1000: ret\n'
        with patch.object(P.subprocess,'check_output',side_effect=output):r=P.elf_scope(binary,self.base/'scope','candidate')
        self.assertIn('UNREVIEWED',r['proof_status']);self.assertEqual(set(r['scopes']),{'var','stddev'})
        self.assertTrue(any('--stop-address=4128' in argv for argv in calls))
        with patch.object(P.subprocess,'check_output',return_value=symbols+symbols),self.assertRaises(ValueError):P.elf_scope(binary,self.base/'ambiguous','candidate')
        with patch.object(P.subprocess,'check_output',return_value=''),self.assertRaises(ValueError):P.elf_scope(binary,self.base/'missing','candidate')

    def test_public_contract_parser_rejects_offset_and_size(self):
        p=self.base/'public';p.mkdir();(p/'index.tsv').write_text('0\t0\t0\t2\t0\t0\t1\t0\t0\t3ff0000000000000\t2\t0\t0\t0\n');(p/'outputs.bin').write_bytes(struct.pack('<Q',P.POISON))
        rows,words,n=C.records(p);self.assertEqual((len(rows),n),(1,1));del words
        (p/'index.tsv').write_text((p/'index.tsv').read_text().rstrip('\n')[:-1]+'1\n')
        with self.assertRaises(AssertionError):C.records(p)
        (p/'outputs.bin').write_bytes(b'')
        with self.assertRaises(AssertionError):C.records(p)

    def test_source_gate_archive_binding_rejects_mutations(self):
        import shutil
        d=self.base/'source-gates';(d/'controller').mkdir(parents=True)
        names={'protocol-tests.log','generator-tests.log','generator-clippy.log','library-tests-and-docs.log','library-clippy.log','regen-check.log','server-build.log','all-indicator-regtests.log'}
        for n in names:(d/n).write_text('PASS '+n+'\n')
        freeze=json.loads((ROOT/'tests/data/var-windows/source-freeze.json').read_text())
        record=dict(complete=True,timing_enabled=False,candidate='a'*40,baseline='b'*40,source_files=freeze['files'],logs={n:P.sha(d/n) for n in names})
        f=d/'source-gates.json';f.write_text(json.dumps(record));(d/'candidate-status.txt').write_bytes(b'');(d/'controller-commit.txt').write_text('c'*40+'\n')
        sources=[p for p in (ROOT/'scripts').glob('*var_windows*') if p.is_file()]+[ROOT/'scripts/VAR_WINDOWS_CI.md',ROOT/'tests/test_var_windows_preflight.py',ROOT/'tests/data/var-windows/source-freeze.json',ROOT/'tests/data/var-windows/normal-codegen-reference.json',ROOT/'tests/test_var_windows_codegen.py']
        for source in sources:shutil.copyfile(source,d/'controller'/source.name)
        shutil.copyfile(ROOT/'.github/workflows/var-windows-preflight.yml',d/'workflow.yml')
        expected=dict(candidate='a'*40,baseline='b'*40)
        with patch.object(P.subprocess,'check_output',return_value='c'*40+'\n'):
            self.assertFalse(P.gate_record(self.base,expected)['record']['timing_enabled'])
            for mutate in (lambda r:r.update(complete=1),lambda r:r.update(timing_enabled=True),lambda r:r.update(candidate='d'*40),lambda r:r['logs'].pop('protocol-tests.log'),lambda r:r['source_files'].update(WRONG='bad')):
                bad=copy.deepcopy(record);mutate(bad);f.write_text(json.dumps(bad))
                with self.assertRaises(ValueError):P.gate_record(self.base,expected)
            f.write_text(json.dumps(record))
            for dest in (d/'workflow.yml',d/'controller/bench_var_windows.rs',d/'protocol-tests.log'):
                old=dest.read_bytes();dest.write_bytes(old+b'changed')
                with self.assertRaises(ValueError):P.gate_record(self.base,expected)
                dest.write_bytes(old)
            (d/'candidate-status.txt').write_text(' M dirty')
            with self.assertRaises(ValueError):P.gate_record(self.base,expected)

    def fake_C(self, force_lookback=None):
        import ctypes, math
        class Fake:
            array_calls=0
            def lookback(self,name,period,dev):
                if force_lookback is not None:return force_lookback
                period=5 if period==-2147483648 else period
                if not (1 if name=='TA_VAR' else 2)<=period<=100000:return -1
                if dev!=-4e37 and (not math.isfinite(dev) or not -3e37<=dev<=3e37):return -1
                return period-1
            def __getattr__(self,name):
                if name.endswith('_Lookback'):return lambda period,dev:self.lookback(name[:-9],period,dev)
                def arrays(start,end,data,period,dev,beg,count,output):
                    self.array_calls+=1;first=max(start,self.lookback(name,period,dev));n=max(0,end-first+1)
                    ctypes.cast(beg,ctypes.POINTER(ctypes.c_int))[0]=first if n else 0
                    ctypes.cast(count,ctypes.POINTER(ctypes.c_int))[0]=n
                    return 0
                return arrays
        return Fake()

    def test_C_capacity_derived_before_array_call(self):
        import numpy as np
        data=np.arange(10,dtype='<f8')
        for cap,beg,count in ((2,0,2),(2,4,6),(10,4,2),(10,0,6)):
            lib=self.fake_C()
            with self.assertRaises(AssertionError):C.checked_C_call(lib,'TA_VAR',data,5,1.,0,9,cap,beg,count)
            self.assertEqual(lib.array_calls,0)
        for name,period,dev in (('TA_VAR',0,1.),('TA_STDDEV',1,1.),('TA_VAR',100001,1.),('TA_VAR',5,float('nan')),('TA_STDDEV',5,float('inf'))):
            lib=self.fake_C()
            with self.assertRaises(AssertionError):C.checked_C_call(lib,name,data,period,dev,0,9,10,4,6)
            self.assertEqual(lib.array_calls,0)
        for lookback in (-1,True,3.5):
            lib=self.fake_C(lookback)
            with self.assertRaises(AssertionError):C.checked_C_call(lib,'TA_VAR',data,5,1.,0,9,10,4,6)
            self.assertEqual(lib.array_calls,0)
        lib=self.fake_C()
        with self.assertRaises(AssertionError):C.checked_C_call(lib,'TA_VAR',data,5,1.,0,10,10,4,7)
        self.assertEqual(lib.array_calls,0)

    def test_C_minimum_default_and_zero_output_controls(self):
        import numpy as np
        data=np.arange(10,dtype='<f8')
        for name,p,dev,start,end,cap,beg,count in [('TA_VAR',1,1.,0,9,10,0,10),('TA_STDDEV',2,1.,0,9,9,1,9),('TA_VAR',-2147483648,-4e37,0,9,6,4,6),('TA_STDDEV',-2147483648,-4e37,0,9,6,4,6),('TA_VAR',14,1.,0,1,0,0,0),('TA_STDDEV',14,1.,0,1,0,0,0),('TA_VAR',5,1.,7,9,3,7,3)]:
            lib=self.fake_C();ret,b,n,out=C.checked_C_call(lib,name,data,p,dev,start,end,cap,beg,count)
            self.assertEqual((ret,b,n,len(out)),(0,beg,count,cap));self.assertEqual(lib.array_calls,1)

    def test_lossless_live_C_full_buffers_and_metadata(self):
        import numpy as np
        directory=self.base/'live';writer=C.RawCWriter(directory)
        first=[0,3,7,2,0,2,3,0,1,0x3ff0000000000000,0,1,2,17]
        second=[1,2,9,1,0,1,2,0,0,0x3ff0000000000000,0,0,2,20]
        values=np.array([0x8000000000000000,0x7ff8000000001234,P.POISON],dtype='<u8')
        writer.append(first,0,1,2,values)
        more=np.array([0x7ff0000000000000,0xfff0000000000000],dtype='<u8')
        writer.append(second,0,0,2,more);record=writer.finish()
        rows=[list(map(int,line.split('\t')))for line in (directory/'index.tsv').read_text().splitlines()]
        self.assertEqual(rows,[first+[0,1,2,0],second+[0,0,2,3]])
        self.assertEqual(tuple(record['fields']),C.RawCWriter.fields);self.assertEqual(len(record['fields']),18)
        self.assertEqual((record['rows'],record['buffer_words']),(2,5))
        expected=struct.pack('<5Q',0x8000000000000000,0x7ff8000000001234,P.POISON,0x7ff0000000000000,0xfff0000000000000)
        self.assertEqual((directory/'outputs.bin').read_bytes(),expected)
        self.assertEqual(record['outputs_sha256'],P.sha(directory/'outputs.bin'));self.assertEqual(record['index_sha256'],P.sha(directory/'index.tsv'))
        with self.assertRaises(AssertionError):writer.append(first,0,1,2,values)
        with self.assertRaises(AssertionError):writer.finish()
        with self.assertRaises(FileExistsError):C.RawCWriter(directory)

    def test_live_C_writer_rejects_invalid_physical_schema_before_write(self):
        import numpy as np
        writer=C.RawCWriter(self.base/'invalid-live');row=[0,2,0,1,0,1,2,0,0,0x3ff0000000000000,0,0,2,0]
        for values in (np.array([1.0,2.0]),np.array([1],dtype='<u8'),np.zeros((1,2),dtype='<u8'),np.zeros(4,dtype='<u8')[::2]):
            with self.assertRaises(AssertionError):writer.append(row,0,0,2,values)
        bad=list(row);bad[0]=True
        with self.assertRaises(AssertionError):writer.append(bad,0,0,2,np.zeros(2,dtype='<u8'))
        self.assertEqual((writer.rows,writer.offset),(0,0));record=writer.finish();self.assertEqual(record['buffer_words'],0)

    def workflow_server_binding(self):
        import ast,hashlib,re,textwrap,tomllib
        workflow=(ROOT/'.github/workflows/var-windows-preflight.yml').read_text()
        blocks=re.findall(r"          python - <<'PY'\n(.*?)\n          PY",workflow,re.S)
        target=[textwrap.dedent(b) for b in blocks if 'def server_binding(' in b]
        self.assertEqual(len(target),1);tree=ast.parse(target[0]);functions=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='server_binding'];self.assertEqual(len(functions),1)
        namespace=dict(Path=Path,re=re,hashlib=hashlib,tomllib=tomllib)
        exec(compile(ast.Module(body=functions,type_ignores=[]),'workflow-server-binding','exec'),namespace)
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='server_binding'];self.assertEqual(len(calls),1)
        return namespace['server_binding']

    def server_fixture(self):
        root=(self.base/'server-source').resolve();logs=self.base/'server-logs';logs.mkdir()
        lines=[]
        for relative,name,version in [('ta_codegen/generator','ta-codegen','0.1.0'),('ta_codegen/output/rust/library','ta-lib','0.8.4'),('ta_codegen/output/rust/tools','ta-lib-tools','0.8.4')]:
            path=root/relative;path.mkdir(parents=True);(path/'Cargo.toml').write_text(f'[package]\nname="{name}"\nversion="{version}"\n')
            lines.append(f'   Compiling {name} v{version} ({path})')
        source=root/'ta_codegen/generator/src/main.rs';source.parent.mkdir();source.write_text('let src = rust_dir.join("target/release/ta_codegen_serve");\n')
        paths=['ta_codegen/generator/target/release/ta_codegen','ta_codegen/output/rust/target/release/ta_codegen_serve','bin/ta_codegen_serve_rust','bin/ta_codegen_serve_c','bin/ta_regtest']
        for n in paths:
            p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'\x7fELF'+(b'RUST'if 'serve_rust' in n or n.endswith('/ta_codegen_serve')else n.encode()))
        (logs/'server-build.log').write_text('\n'.join(lines)+'\n')
        (logs/'all-indicator-regtests.log').write_text('All 2 language(s) passed codegen verification\n│ C │ 237 │ 0 │ 123 │\n│ Rust │ 237 │ 0 │ 456 │\n* All tests succeeded. Enjoy the library. *\n')
        return root,logs

    def test_actual_workflow_server_copy_binding(self):
        function=self.workflow_server_binding();root,logs=self.server_fixture();commit='4f73a88c554e8482fc566c2f351bca94b45946ab';rust='rustc 1.97.0 (fixture)\nhost: x86_64-unknown-linux-gnu\n'
        result=function(root,logs,commit,commit,rust,'cc fixture')
        self.assertEqual(result['binaries']['Rust_built']['sha256'],result['binaries']['Rust_installed']['sha256']);self.assertEqual(result['runtime_counts'],{'C':[237,0],'Rust':[237,0]})
        self.assertEqual(result['command'][:5],['env','-u','CARGO_TARGET_DIR','-u','CARGO_BUILD_BUILD_DIR'])
        # Exact same source workflow function rejects stale/missing/wrong copies.
        for relative in ['bin/ta_codegen_serve_rust','ta_codegen/output/rust/target/release/ta_codegen_serve','bin/ta_regtest']:
            p=root/relative;old=p.read_bytes();p.write_bytes(b'WRONG')
            with self.assertRaises(AssertionError):function(root,logs,commit,commit,rust,'cc')
            p.write_bytes(old)
        p=root/'bin/ta_codegen_serve_rust';old=p.read_bytes();p.write_bytes(b'\x7fELFDIFFERENT')
        with self.assertRaises(AssertionError):function(root,logs,commit,commit,rust,'cc')
        p.write_bytes(old)
        for actual,version in [('0'*40,rust),(commit,rust.replace('1.97.0','1.90.0')),(commit,rust.replace('x86_64-unknown-linux-gnu','aarch64-apple-darwin'))]:
            with self.assertRaises(AssertionError):function(root,logs,commit,actual,version,'cc')
        p=root/'ta_codegen/generator/src/main.rs';p.write_text('wrong copy contract')
        with self.assertRaises(AssertionError):function(root,logs,commit,commit,rust,'cc')

    def test_workflow_runtime_and_fresh_compile_negatives(self):
        function=self.workflow_server_binding();root,logs=self.server_fixture();commit='4f73a88c554e8482fc566c2f351bca94b45946ab';rust='rustc 1.97.0 (fixture)\nhost: x86_64-unknown-linux-gnu\n'
        p=logs/'server-build.log';old=p.read_text()
        for bad in [old.replace(str(root),'/wrong/source'),old.replace('ta-lib v0.8.4','ta-lib v9.9.9'),old+old.splitlines()[0]+'\n','\n'.join(old.splitlines()[1:]),'\x1b[1G'+old]:
            p.write_text(bad)
            with self.assertRaises(AssertionError):function(root,logs,commit,commit,rust,'cc')
        p.write_text('\x1b[32m'+old+'\x1b[0m');self.assertEqual(function(root,logs,commit,commit,rust,'cc')['runtime_counts']['C'],[237,0]);p.write_text(old)
        p=logs/'all-indicator-regtests.log';old=p.read_text()
        for bad in [old.replace('│ C │ 237','│ C │ 236'),old.replace('│ Rust │ 237 │ 0','│ Rust │ 237 │ 1'),old+'│ Rust │ 237 │ 0 │ 456 │\n',old+'│ Rust │ 237 │ 1 │ 456 │\n',old+'│ C │ malformed │ row │\n',old.replace('All 2 language(s) passed codegen verification','missing'),old.replace('All tests succeeded. Enjoy the library.','missing')]:
            p.write_text(bad)
            with self.assertRaises(AssertionError):function(root,logs,commit,commit,rust,'cc')
        p.write_text(old)
        workflow=(ROOT/'.github/workflows/var-windows-preflight.yml').read_text()
        self.assertEqual(workflow.count('env -u CARGO_TARGET_DIR -u CARGO_BUILD_BUILD_DIR python scripts/build.py servers --language=c,rust'),1)
        self.assertNotIn('export CARGO_TARGET_DIR="$PWD/target-server"',workflow)
        self.assertIn('export CARGO_TARGET_DIR="$PWD/target-generator"',workflow);self.assertIn('export CARGO_TARGET_DIR="$PWD/target-library"',workflow)

    def test_explicit_pointer_and_gate_before_clock_source(self):
        text=(ROOT/'scripts/bench_var_windows.rs').read_text()
        self.assertEqual(text.count('const TIMING_ENABLED:bool=true;'),1)
        for target,kind in [('Core::var','VarianceFn'),('Core::stddev','VarianceFn'),('capi::TA_VAR','CVarianceFn'),('capi::TA_STDDEV','CVarianceFn')]:
            self.assertIn('black_box('+target+' as '+kind+')',text)
        self.assertEqual(text.count('let invoke=black_box(sample as SampleFn);'),2)
        self.assertIn('if a.len()==5 {assert_eq!(a[4],"--capture-only")',text)
        preflight=(ROOT/'scripts/var_windows_preflight.py').read_text()
        self.assertNotIn("'--golden',",preflight)
        self.assertIn('timings_collected=False',preflight)
        workflow=(ROOT/'.github/workflows/var-windows-preflight.yml').read_text()
        self.assertLess(workflow.index('run: evidence-env/bin/python control-source/scripts/var_windows_codegen.py'),workflow.index('evidence-env/bin/python control-source/scripts/var_windows_timed.py'))

    def test_samples_strict_and_orders(self):
        c=self.spec['cases'][0]
        row=dict(case=c['name'],n=c['rows'],iterations=c['iterations'],repeats=31,warmups=5,checked_values=c['rows']-c['period']+1,samples_ms=[1.]*31)
        T.sample_record(row,c)
        for key,value in [('n',True),('iterations',True),('samples_ms',[1.]*30),('samples_ms',[True]*31),('samples_ms',[float('nan')]*31),('samples_ms',[0.]*31),('checked_values',0)]:
            bad=copy.deepcopy(row);bad[key]=value
            with self.assertRaises(ValueError):T.sample_record(bad,c)
        from collections import Counter
        self.assertEqual(len(T.ORDERS),12);self.assertEqual(set(Counter(T.ORDERS).values()),{2})
        self.assertEqual(12*16*3,576);self.assertEqual(576*31,17856)

    def test_complete_lossless_child_bytes(self):
        import gzip
        p=self.base/'child.bin';raw=b'VAROUT01'+bytes(range(256))*2;p.write_bytes(raw)
        record=T.compress_complete(p,raw)
        self.assertFalse(p.exists());self.assertEqual(gzip.decompress(Path(record['path']).read_bytes()),raw)
        p.write_bytes(raw)
        with self.assertRaises(ValueError):T.compress_complete(p,raw)
        p.write_bytes(raw+b'changed')
        with self.assertRaises(ValueError):T.compress_complete(p,raw)

    def test_all48_process_distributions_and_losses(self):
        records=[]
        for i,order in enumerate(T.ORDERS):
            for c in self.spec['cases']:
                for arm in order:records.append(dict(case=c['name'],arm=arm,round=i,samples_ms=[{'original':1.,'baseline':2.,'candidate':3.}[arm]]*31))
        rows=T.comparisons(records,self.spec);self.assertEqual(len(rows),48)
        for row in rows:
            self.assertEqual(row['slower_pairs'],12);self.assertEqual(row['faster_pairs'],0)
            self.assertEqual(row['numerator_process_distribution_ms']['count'],12)
            self.assertEqual(row['numerator_pooled_sample_ms']['count'],372)
            self.assertEqual(len(row['numerator_process_medians_ms']),12)
            self.assertEqual(row['description'],'paired-ratio p10>1.03')
            self.assertEqual(row['duration_unit'],'whole iteration-batch milliseconds')
        with self.assertRaises(ValueError):T.comparisons(records[:-1],self.spec)

    def test_actual_gate_rejects_all_identity_changes_before_clock(self):
        out=self.base;binary=out/'binary';binary.write_bytes(b'actual product');proof=out/'proof';proof.write_bytes(b'actual scoped proof')
        (out/'preflight.json').write_text('preflight')
        p=dict(pins={'a':'source'},runtime={'profile':'release'},timer_body_compiled=True,timings_collected=False,binaries={a:dict(path=str(binary),sha256=P.sha(binary),description=dict(timing_enabled=True,opaque_fnptr=True,pointer_bytes=8))for a in T.ARMS})
        g=dict(timing_allowed=True,rust_version='1.90.0',preflight_sha256=P.sha(out/'preflight.json'),source_commits=p['pins'],profile='release',binary_sha256={a:P.sha(binary)for a in T.ARMS},codegen_module_sha256=P.sha(ROOT/'scripts/var_windows_codegen.py'),reference_sha256=P.sha(ROOT/'tests/data/var-windows/normal-codegen-reference.json'),files={'proof':P.sha(proof)})
        path=out/'enabled-elf-gate.json';path.write_text(json.dumps(g));T.require_gate(out,'1.90.0',p)
        changes=[lambda v:v.update(timing_allowed=False),lambda v:v.update(timing_allowed=1),lambda v:v.update(rust_version='1.97.0'),lambda v:v.update(preflight_sha256='bad'),lambda v:v.update(profile='different'),lambda v:v.update(source_commits={}),lambda v:v.update(binary_sha256={}),lambda v:v.update(codegen_module_sha256='bad'),lambda v:v.update(reference_sha256='bad'),lambda v:v.update(files={}),lambda v:v.update(files={'../escape':'bad'}),lambda v:v.update(files={'proof':'bad'})]
        for change in changes:
            bad=copy.deepcopy(g);change(bad);path.write_text(json.dumps(bad))
            with self.assertRaises(ValueError):T.require_gate(out,'1.90.0',p)
        path.write_text(json.dumps(g));binary.write_bytes(b'changed')
        with self.assertRaises(ValueError):T.require_gate(out,'1.90.0',p)


if __name__=='__main__':unittest.main()
