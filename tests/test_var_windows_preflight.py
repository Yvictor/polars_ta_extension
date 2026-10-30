"""Negative source/static protocol checks; no kernel timing or product import."""
import copy
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
P = load('var_windows_preflight')
C = load('var_windows_contract')


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
        sources=[p for p in (ROOT/'scripts').glob('*var_windows*') if p.is_file()]+[ROOT/'scripts/VAR_WINDOWS_CI.md',ROOT/'tests/test_var_windows_preflight.py',ROOT/'tests/data/var-windows/source-freeze.json']
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

    def test_timer_disabled_in_actual_source(self):
        text=(ROOT/'scripts/bench_var_windows.rs').read_text()
        self.assertEqual(text.count('const TIMING_ENABLED:bool=false;'),1)
        self.assertIn('assert!(TIMING_ENABLED,"Timing blocked',text)
        self.assertIn('black_box(Core::var)',text);self.assertIn('black_box(capi::TA_VAR)',text)
        self.assertIn('if a.len()==5 {assert_eq!(a[4],"--capture-only")',text)

    def test_no_prospective_protocol_is_current_measurement(self):
        text=(ROOT/'scripts/var_windows_preflight.py').read_text()
        self.assertNotIn("'--golden',",text)
        self.assertIn('timing_enabled=False',text)
        self.assertIn("description['timing_enabled'] is False",text)


if __name__=='__main__':unittest.main()
