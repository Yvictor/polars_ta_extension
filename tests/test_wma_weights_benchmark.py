"""Protocol validation only: these tests never run a kernel timer."""
import copy
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import shutil
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('wma_weights_benchmark',ROOT/'scripts/wma_weights_benchmark.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class Protocol(unittest.TestCase):
    def sample(self):
        return {'case':'wma_14_100','n':100,'iterations':1000,'repeats':31,'warmups':5,'checked_values':87,'samples_ms':[.001]*31}

    def test_fixed_inventory_and_balanced_orders(self):
        self.assertEqual(len(m.CASES),15);self.assertEqual(len(set(m.CASES)),15)
        self.assertEqual(m.CASES[8:11],(('mavp',30,100),('mavp',30,10000),('mavp',30,1000000)))
        self.assertEqual(len(m.ORDERS),12);self.assertEqual(len(m.C_ORDERS),12)
        for arm in m.PRIMARY:
            for position in range(3):self.assertEqual(sum(o[position]==arm for o in m.ORDERS),4)
        for arm in m.C_PAIR:
            for position in range(2):self.assertEqual(sum(o[position]==arm for o in m.C_ORDERS),6)
        self.assertEqual(15*(sum(map(len,m.ORDERS))+sum(map(len,m.C_ORDERS))),900)

    def test_strict_json(self):
        for invalid in ('{"x":1,"x":2}','{"x":NaN}','{"x":Infinity}'):
            with self.assertRaises(ValueError):m.read_json(invalid)
        self.assertEqual(m.read_json('{"x":1}'),{'x':1})

    def test_sample_positive_and_negative(self):
        m.validate_sample(self.sample(),('wma',14,100))
        changes={'n':True,'iterations':1,'repeats':30,'warmups':True,'checked_values':86,'case':'bank_30_10000','samples_ms':[.001]*30}
        for key,value in changes.items():
            s=self.sample();s[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):m.validate_sample(s,('wma',14,100))
        for x in (0.,-1.,float('nan'),float('inf'),True):
            s=self.sample();s['samples_ms'][0]=x
            with self.subTest(x=x),self.assertRaises(ValueError):m.validate_sample(s,('wma',14,100))
        s=self.sample();s['extra']=1
        with self.assertRaises(ValueError):m.validate_sample(s,('wma',14,100))

    def test_exact_numeric_policy(self):
        pack=lambda x:struct.pack('<d',x)
        self.assertEqual(m.compare_words(pack(1.),pack(1.)),0)
        with self.assertRaises(ValueError):m.compare_words(pack(0.),pack(-0.))
        with self.assertRaises(ValueError):m.compare_words(pack(1.),pack(1.0000000000000002))
        with self.assertRaises(ValueError):m.compare_words(pack(float('inf')),pack(float('-inf')))
        with self.assertRaises(ValueError):m.compare_words(pack(float('nan')),pack(1.))
        self.assertEqual(m.compare_words(struct.pack('<Q',0x7ff8000000000001),struct.pack('<Q',0xfff8000000000002)),1)

    def test_capture_shape_finite_and_raw_tail(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'out';header=b'WMAOUT01'+struct.pack('<QQQ',100,13,87)
            good=header+struct.pack('<87d',*range(87))+struct.pack('<Q',m.CANARY)*21
            p.write_bytes(good);self.assertEqual(m.capture(p,('wma',14,100)),good)
            for bad in (good[:-1],good+b'x',b'INVALID!'+good[8:],good[:16]+struct.pack('<Q',12)+good[24:],good[:-8]+struct.pack('<Q',0x7ff8000000000000),good[:32]+struct.pack('<d',float('inf'))+good[40:]):
                p.write_bytes(bad)
                with self.assertRaises(ValueError):m.capture(p,('wma',14,100))

    def test_fixture_physical_layout(self):
        with tempfile.TemporaryDirectory() as d:
            r=m.fixture(Path(d),100);p=Path(r['path']);data=p.read_bytes()
            self.assertEqual(len(data),16+24*100);self.assertEqual(data[:8],b'WMAFIX01');self.assertEqual(struct.unpack('<Q',data[8:16]),(100,))
            periods=struct.unpack('<100d',data[16+800:16+1600]);self.assertEqual(periods[:8],(2.,7.,14.,30.)*2)
            self.assertEqual(m.sha(p),r['sha256'])

    def test_report_requires_all_processes_and_keeps_sections(self):
        rows=[]
        for section,orders in (('primary',m.ORDERS),('C-pair',m.C_ORDERS)):
            for round,order in enumerate(orders):
                for c in m.CASES:
                    for arm in order:
                        rows.append({'section':section,'round':round,'case':'_'.join(map(str,c)),'arm':arm,'samples_ms':[2. if arm in ('candidate','candidate-c') else 1.]*31})
        r=m.report(rows);self.assertEqual(len(r),60)
        self.assertTrue(all(x['ratio_distribution']['median']==2. for x in r if x['ratio'].startswith('candidate')))
        self.assertTrue(all(x['classification']=='consistent slower' for x in r if x['ratio'].startswith('candidate')))
        with self.assertRaises(ValueError):m.report(rows[:-1])

    def test_actual_symbol_forms_and_unknown_rejection(self):
        headers=[
            '00000000 <ta_lib::ta_func::wma::_$LT$impl$u20$ta_lib..ta_func..types..Core$GT$::wma::h123>:',
            '00000000 <<ta_lib::ta_func::types::Core>::wma>:',
            '00000000 <<ta_lib::ta_func::wma::WmaStream>::update>:',
            '00000000 <ta_lib::ta_func::wma::WmaStream::update::h123>:',
            '00000000 <TA_WMA>:',
            '00000000 <TA_MAVP_Update>:',
        ]
        for header in headers:
            with self.subTest(header=header):
                scopes=m.assembly_scopes(header+'\n  00: punpckldq %xmm1,%xmm2\n00000001 <unrelated>:\n  01: ret\n')
                self.assertEqual(len(scopes),1)
                self.assertEqual(len(next(iter(scopes.values()))),2)
        with self.assertRaises(ValueError):m.assembly_scopes('00000000 <unrelated>:\n  00: ret\n')

    def test_source_gate_exact_logs_and_controller_binding(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);g=out/'source-gates';g.mkdir();(g/'controller').mkdir()
            for name in m.GATE_LOGS:(g/name).write_text('passed '+name+'\n')
            for name,canonical in m.gate_bindings().items():shutil.copyfile(canonical,g/name)
            commit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
            (g/'controller-commit.txt').write_text(commit+'\n');(g/'candidate-status.txt').write_bytes(b'')
            record={'complete':True,'candidate':m.CANDIDATE,'toolchain':'1.97.0','library_msrv':'1.88','source_files':json.loads((m.PROOF/'source-freeze.json').read_text())['files'],'logs':{n:m.sha(g/n) for n in m.GATE_LOGS}}
            def write(r): (g/'source-gates.json').write_text(json.dumps(r))
            write(record);self.assertEqual(m.gate_record(out)['controller_commit'],commit)
            for bad in ('missing','substituted','empty','wrong-hash','wrong-head','wrong-msrv','wrong-controller','wrong-workflow'):
                write(record);(g/'controller-commit.txt').write_text(commit+'\n')
                for name,canonical in m.gate_bindings().items():shutil.copyfile(canonical,g/name)
                (g/'protocol-tests.log').write_text('passed protocol-tests.log\n')
                r=copy.deepcopy(record)
                if bad=='missing':r['logs'].pop('protocol-tests.log')
                elif bad=='substituted':r['logs']['unrelated.log']=r['logs'].pop('protocol-tests.log')
                elif bad=='empty':(g/'protocol-tests.log').write_bytes(b'');r['logs']['protocol-tests.log']=m.sha(g/'protocol-tests.log')
                elif bad=='wrong-hash':r['logs']['protocol-tests.log']='0'*64
                elif bad=='wrong-head':(g/'controller-commit.txt').write_text('0'*40)
                elif bad=='wrong-msrv':r['library_msrv']='1.90'
                elif bad=='wrong-controller':(g/'controller/bench_wma_weights.rs').write_text('changed')
                elif bad=='wrong-workflow':(g/'workflow.yml').write_text('changed')
                write(r)
                with self.subTest(bad=bad),self.assertRaises(ValueError):m.gate_record(out)

    def test_exact_cargo_fingerprint_layouts(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)
            legacy=target/'release/.fingerprint'
            modern=target/'build-dir/release/.fingerprint'
            # No fallback: metadata in the other compiler layout cannot satisfy a missing product.
            for version in ('1.90.0','1.97.0','1.96.0'):
                with self.assertRaises(ValueError):m.fingerprint_directory(target,version)
            for folder in (legacy,modern):
                (folder/'unrelated-123').mkdir(parents=True)
                (folder/'unrelated-123/lib-unrelated.json').write_text('{}')
            for version in ('1.90.0','1.97.0'):
                with self.assertRaises(ValueError):m.fingerprint_directory(target,version)
            for version,folder in (('1.90.0',legacy),('1.97.0',modern)):
                package=folder/'ta-lib-123';package.mkdir();metadata=package/'lib-ta_lib.json';metadata.write_text('{}')
                self.assertEqual(m.fingerprint_directory(target,version),folder)
                metadata.write_bytes(b'')
                with self.assertRaises(ValueError):m.fingerprint_directory(target,version)
                metadata.write_text('{}')
            shutil.rmtree(modern)
            with self.assertRaises(ValueError):m.fingerprint_directory(target,'1.97.0')
            self.assertEqual(m.fingerprint_directory(target,'1.90.0'),legacy)

    def test_reviewed_freeze(self):
        f=json.loads((m.PROOF/'source-freeze.json').read_text())
        self.assertEqual(f['commit'],m.CANDIDATE);self.assertEqual(f['base'],m.BASELINE);self.assertEqual(len(f['files']),14)
        self.assertNotEqual(m.CANDIDATE,m.BASELINE);self.assertNotEqual(m.CANDIDATE,m.ORIGINAL)
        for name,h in f['proofs'].items():self.assertEqual(m.sha(m.PROOF/name),h)


if __name__=='__main__':unittest.main()
