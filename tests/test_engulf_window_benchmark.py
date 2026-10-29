"""Fail-closed tests for the isolated kernel protocol; no kernel timers run."""
import collections
import importlib.util
import json
from pathlib import Path
import struct
import sys
import tarfile
import tempfile
import types
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import engulf_window_benchmark as b


def selected_bytes(indicator,n):
    beg,count=b.shape(indicator,n)
    values=[0]*beg+[0]*count+[b.CANARY]*8
    return b'ENGOUT01'+struct.pack('<QQQ',n,beg,count)+struct.pack('<'+'i'*(n+8),*values)


def record(indicator,n,s,e):
    beg,count=b.shape(indicator,n,s,e)
    values=[0]*beg+[0]*count+[b.CANARY]*(n+8-beg-count)
    return b'ENGOUT01'+struct.pack('<QQQ',n,beg,count)+struct.pack('<'+'i'*(n+8),*values)


def output(selection,arm,timed):
    ind,fixture,n,mode=selection;identity=dict(indicator=ind,fixture=fixture,n=n,mode=mode)
    if not timed:return json.dumps(dict(kind='capture',**identity,edge_records=9,range_errors=3,short_checks=0 if arm=='original' else 5,timed=False))
    return '\n'.join(map(json.dumps,[dict(kind='validation',**identity,beg=b.shape(ind,n)[0],count=b.shape(ind,n)[1],golden_verified=True),dict(kind='case',**identity,iterations=b.ITERS[n],warmups=5,samples_ns=[100+len(arm)]*31)]))


class Protocol(unittest.TestCase):
    def test_unset_candidate_blocks_before_files_or_build(self):
        with tempfile.TemporaryDirectory() as d,patch.object(b,'build') as build,patch.object(b,'CANDIDATE','UNSET_CANDIDATE_DO_NOT_RUN'):
            target=Path(d)/'not-created'
            with self.assertRaisesRegex(ValueError,'unset'):
                b.main(['--original-source',d,'--baseline-source',d,'--candidate-source',d,'--candidate-commit','a'*40,'--output',str(target),'--codegen-proof',d,'--build-only'])
            self.assertFalse(target.exists());build.assert_not_called()

    def test_inventory_balance(self):
        self.assertEqual(len(b.CASES),18);self.assertEqual(len(set(b.CASES)),18)
        self.assertEqual(len(b.MODES),2);self.assertEqual(len(b.ORDERS),12)
        self.assertEqual(set(collections.Counter(b.ORDERS).values()),{2})
        for arm in b.ARMS:
            self.assertEqual(collections.Counter(o.index(arm) for o in b.ORDERS),{0:4,1:4,2:4})
        self.assertEqual(18*2*3*12,1296);self.assertEqual(1296*31,40176)

    def test_exact_types_and_json(self):
        for text in ['{"a":1,"a":2}','{"a":NaN}']:
            with self.assertRaises(ValueError):b.read_json(text)
        self.assertFalse(b.exact({'x':True},{'x':1}));self.assertFalse(b.exact({'x':[False]},{'x':[0]}))

    def test_stdout_modes_and_identity(self):
        sel=('engulf','white',100,'typed')
        for arm in b.ARMS:
            for timed in (True,False):b.parse(output(sel,arm,timed),sel,arm,timed)
        text=output(sel,'baseline',True)
        for bad in [text.splitlines()[1],text+'\n'+text,text.replace('"typed"','"abstract"'),text.replace('"n": 100','"n": true'),text.replace('"golden_verified": true','"golden_verified": 1'),text.replace('"warmups": 5','"warmups": 4'),text.replace('"iterations": 1000','"iterations": 1')]:
            with self.subTest(bad=bad),self.assertRaises(ValueError):b.parse(bad,sel,'baseline',True)
        for samples in ([1]*30,[1]*30+[0],[1]*30+[True],[1]*30+[float('inf')]):
            lines=text.splitlines();r=json.loads(lines[1]);r['samples_ns']=samples
            with self.assertRaises(ValueError):b.parse(lines[0]+'\n'+json.dumps(r),sel,'baseline',True)
        capture=json.loads(output(sel,'baseline',False));capture['short_checks']=True
        with self.assertRaises(ValueError):b.parse(json.dumps(capture),sel,'baseline',False)

    def test_physical_tail_range_and_inventory(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'capture';good=b''.join(record('doji',64,s,e) for s,e in b.EDGES)+selected_bytes('doji',100);p.write_bytes(good)
            r=b.capture(p,'doji',100,True);self.assertEqual(r['records'],10);self.assertEqual(r['selected'],selected_bytes('doji',100))
            for bad in [good[:-1],good+b'x',b'X'+good[1:],good[:8]+struct.pack('<Q',65)+good[16:],good[:-4]+struct.pack('<i',0)]:
                p.write_bytes(bad)
                with self.assertRaises(ValueError):b.capture(p,'doji',100,True)

    def test_selected_command_only_one_case(self):
        p={'arms':{'candidate':{'binary':'candidate'}},'inputs':{'white/100':{'path':'input'}}}
        self.assertEqual(b.child_command(p,'candidate',('engulf','white',100,'abstract'),'actual','golden'),['candidate','engulf','white','abstract','100','1000','input','actual','--golden','golden'])

    def fake_execute(self,command,stem,timeout):
        arm=command[0];sel=(command[1],command[2],int(command[4]),command[3]);timed=command[8]=='--golden'
        self.events.append((timed,arm,sel));Path(command[7]).write_bytes(b'selected')
        return output(sel,arm,timed),{'minor':0,'major':0}

    def fake_capture(self,path,indicator,n,full):
        return dict(sha256=b.sha(path),bytes=8,records=10 if full else 1,ranges=[],selected=b'selected')

    def protocol_args(self,d):
        p={'arms':{arm:{'binary':arm} for arm in b.ARMS},'inputs':{f'{fixture}/{n}':{'path':'input'} for _,fixture,n in b.CASES}}
        return types.SimpleNamespace(output=Path(d)),p

    def test_production_orchestration_all_captures_before_1296_children(self):
        with tempfile.TemporaryDirectory() as d:
            args,p=self.protocol_args(d);self.events=[]
            with patch.object(b,'execute',self.fake_execute),patch.object(b,'capture',self.fake_capture),patch.object(b,'check_hits'):
                validation=b.prepare(args,p);report=b.measure(args,p,validation)
            self.assertEqual(len(self.events),108+1296);self.assertTrue(all(not e[0] for e in self.events[:108]));self.assertTrue(all(e[0] for e in self.events[108:]))
            self.assertEqual(report['children'],1296);self.assertEqual(report['samples'],40176);self.assertEqual(len(report['results']),36)
            at=108
            for case in b.CASES:
                for mode in b.MODES:
                    for order in b.ORDERS:
                        self.assertEqual(tuple(e[1] for e in self.events[at:at+3]),order);self.assertTrue(all(e[2]==(*case,mode) for e in self.events[at:at+3]));at+=3
            proofs=list((Path(d)/'children').glob('*-proof.json'));self.assertEqual(len(proofs),1296)
            self.assertEqual(len((Path(d)/'completed-children.jsonl').read_text().splitlines()),1296)
            self.assertFalse(list((Path(d)/'children').glob('*.bin')))
            self.assertTrue(report['negative_cases'])
            for pairs in report['results'].values():self.assertEqual(len(pairs),3)

    def test_third_arm_capture_mismatch_stops_before_timers(self):
        with tempfile.TemporaryDirectory() as d:
            args,p=self.protocol_args(d);self.events=[]
            def changed(c,s,t):
                result=self.fake_execute(c,s,t)
                if c[0]=='candidate':Path(c[7]).write_bytes(b'changed!')
                return result
            with patch.object(b,'execute',changed),patch.object(b,'capture',self.fake_capture),patch.object(b,'check_hits'),self.assertRaisesRegex(ValueError,'capture mismatch'):b.prepare(args,p)
            self.assertEqual(len(self.events),3);self.assertFalse(any(e[0] for e in self.events));self.assertFalse((Path(d)/'children').exists())

    def test_golden_mutation_stops_measurement(self):
        with tempfile.TemporaryDirectory() as d:
            args,p=self.protocol_args(d);self.events=[]
            with patch.object(b,'execute',self.fake_execute),patch.object(b,'capture',self.fake_capture),patch.object(b,'check_hits'):validation=b.prepare(args,p)
            Path(next(iter(validation['goldens'].values()))['path']).write_bytes(b'wrong')
            with self.assertRaisesRegex(ValueError,'golden changed'):b.measure(args,p,validation)
            self.assertEqual(len(self.events),108)

    def test_missing_capture_gate_and_round_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):b.measure(types.SimpleNamespace(output=Path(d)),{},dict(completed_before_any_timing=True,checks=[]))
        with self.assertRaises(ValueError):b.summarize([])

    def test_child_failure_preserves_output_and_command(self):
        with tempfile.TemporaryDirectory() as d:
            stem=Path(d)/'failure'
            with self.assertRaises(Exception):b.execute([sys.executable,'-c','import sys;print("saved");sys.stderr.write("why");sys.exit(2)'],stem,5)
            self.assertIn('saved',Path(str(stem)+'.stdout').read_text());self.assertIn('why',Path(str(stem)+'.stderr').read_text());self.assertTrue(Path(str(stem)+'-failure.json').exists());self.assertTrue(Path(str(stem)+'-command.json').exists())

    def test_hit_class_guard_and_positive_doji(self):
        with self.assertRaises(ValueError):b.check_hits(selected_bytes('engulf',100),'engulf','alternating',100)
        with self.assertRaises(ValueError):b.check_hits(selected_bytes('doji',100),'doji','white',100)
        b.check_hits(selected_bytes('engulf',100),'engulf','white',100)

    def test_workflow_gates_precede_timing(self):
        workflow=(Path(__file__).resolve().parents[1]/'.github/workflows/engulf-window.yml').read_text()
        self.assertLess(workflow.index('Require reviewed immutable candidate'),workflow.index('uses: actions/checkout'))
        self.assertIn('CANDIDATE_COMMIT: '+b.CANDIDATE,workflow)
        self.assertLess(workflow.index('all C and Rust indicator gates'),workflow.index('All108 complete'))
        self.assertIn('cancel-in-progress: false',workflow)
        self.assertIn('include-hidden-files: true',workflow)

    def test_proof_inventory_nonempty_complete_and_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            with self.assertRaises(ValueError):b.file_inventory(root)
            (root/'manifest.json').write_text('{}');(root/'asm').write_text('proof')
            before=b.file_inventory(root);self.assertEqual(len(before),2);self.assertIn(str(root/'manifest.json'),before)
            (root/'asm').write_text('changed');self.assertNotEqual(before,b.file_inventory(root))
            (root/'unexpected').write_text('extra');self.assertNotEqual(before.keys(),b.file_inventory(root).keys())

    def test_doji_source_control_equality(self):
        k='ta_codegen/output/rust/library/src/ta_func/cdldoji.rs';sources={a:{'source_files':{k:'same'}} for a in ('baseline','candidate')}
        b.check_control_sources(sources);sources['candidate']['source_files'][k]='different'
        with self.assertRaises(ValueError):b.check_control_sources(sources)

    def test_wrong_full_candidate_pin_rejected(self):
        with self.assertRaises(ValueError):b.pins(types.SimpleNamespace(candidate_commit='a'*40))

    def test_build_proof_provenance_does_not_point_to_last_archive(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);out=root/'out';original=root/'original';vendor=original/'talib-sys/vendor';vendor.mkdir(parents=True);archive=vendor/'ta-lib-0.8.1-src.tar.gz'
            with tarfile.open(archive,'w:gz'):pass
            proof=root/'proof';proof.mkdir();(proof/'manifest.json').write_text('{}');(proof/'asm').write_text('assembly')
            args=types.SimpleNamespace(output=out,original_source=original,baseline_source=root/'baseline',candidate_source=root/'candidate',candidate_commit=b.CANDIDATE,harness=b.HERE/'bench_engulf_window.rs',codegen_proof=proof)
            def command(c,log,cwd=None):
                if c[0]=='cmake':
                    (out/'c-build').mkdir(exist_ok=True);(out/'c-build/CMakeCache.txt').write_text('cache');(out/'c-install/lib').mkdir(parents=True,exist_ok=True);(out/'c-install/lib/libta-lib.a').write_bytes(b'C')
                elif c[0]=='cargo':
                    target=Path(c[c.index('--target-dir')+1]);(target/'release').mkdir(parents=True);(target/'release/libta_lib.rlib').write_bytes(b'rlib')
                elif c[0]=='rustc':Path(c[c.index('-o')+1]).write_bytes(b'binary')
            def git_archive(c,check):Path(c[c.index('-o')+1]).write_bytes(b'archive')
            with patch.object(b,'runtime',return_value={}),patch.object(b,'source_record',return_value={}),patch.object(b,'check_codegen_proof'),patch.object(b,'check_control_sources'),patch.object(b,'C_SHA',b.sha(archive)),patch.object(b,'command_run',command),patch.object(b,'fixtures',return_value={}),patch.object(b.subprocess,'run',git_archive),patch.object(b,'verify'):
                b.build(args)
            result=b.read_json((out/'build-provenance.json').read_text())
            self.assertEqual(result['codegen_proof'],b.file_inventory(out/'codegen-proof'));self.assertEqual(len(result['codegen_proof']),2)
            self.assertEqual(len(result['source_archives']),3)
            self.assertIn(str(out/'codegen-proof/manifest.json'),result['codegen_proof'])

    def test_static_proof_is_source_bound(self):
        proof=Path(__file__).parent/'data/engulf-window-codegen';manifest=b.read_json((proof/'manifest.json').read_text());g=b.read_json((proof/'source-gates.json').read_text());cfg=b.read_json((proof/'expanded-cfg-proof.json').read_text());key='ta_codegen/output/rust/library/src/ta_func/cdlengulfing.rs'
        sources={'baseline':{'source_files':{key:cfg['original_source_sha256']}},'candidate':{'source_files':g['source_files']}}
        with patch.object(b,'CANDIDATE',manifest['candidate_commit']):b.check_codegen_proof(proof,sources)
        sources['candidate']['source_files']=dict(g['source_files']);sources['candidate']['source_files'][key]='0'*64
        with patch.object(b,'CANDIDATE',manifest['candidate_commit']),self.assertRaises(ValueError):b.check_codegen_proof(proof,sources)

if __name__=='__main__':unittest.main()
