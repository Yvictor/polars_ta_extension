"""Fail-closed focused kernel protocol tests; no real kernel timers run."""
import collections,json,struct,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import sarext_window_benchmark as b
import sarext_window_codegen as cg


def record(ind,n,s=0,e=None,changes=None):
    beg,count=b.shape(ind,n,s,e);v=[0x3ff0000000000000]*count+[b.CANARY]*(n+8-count)
    for i,x in (changes or {}).items():v[i]=x
    return b'SAROUT01'+struct.pack('<QQQ',n,beg,count)+struct.pack('<'+'Q'*(n+8),*v)


def full(ind,n):return b''.join(record(ind,64,s,e) for _ in range(18) for s,e in b.EDGES)+record(ind,n)


def output(sel,arm,timed):
    ind,fixture,n,mode=sel;identity=dict(indicator=ind,fixture=fixture,n=n,mode=mode)
    if not timed:return json.dumps(dict(kind='capture',**identity,edge_records=180,range_errors=3,parameter_errors={'sar':6,'sarext':24,'add':0}[ind],short_checks=0 if arm=='original' else 3,hardware_fma=False,timed=False))
    return '\n'.join(map(json.dumps,[dict(kind='validation',**identity,beg=b.shape(ind,n)[0],count=b.shape(ind,n)[1],golden_verified=True,hardware_fma=False),dict(kind='case',**identity,iterations=b.ITERS[n],warmups=5,samples_ns=[100+len(arm)]*31)]))


class Protocol(unittest.TestCase):
    def test_unset_before_build_or_files(self):
        with tempfile.TemporaryDirectory()as d,patch.object(b,'build')as build,patch.object(b,'CANDIDATE','UNSET'):
            target=Path(d)/'new'
            with self.assertRaisesRegex(ValueError,'unset'):
                b.main(['--rust-version','1.97.0','--original-source',d,'--baseline-source',d,'--candidate-source',d,'--candidate-commit','a'*40,'--output',str(target),'--codegen-proof',d,'--build-only'])
            self.assertFalse(target.exists());build.assert_not_called()

    def test_preserved_library_is_accepted_by_real_extern_loader(self):
        with tempfile.TemporaryDirectory()as d:
            root=Path(d);source=root/'fixture.rs';source.write_text('pub fn probe() {}\n')
            lib=root/'libfixture.rlib'
            b.subprocess.run(['rustc','--crate-name','fixture','--crate-type','rlib',str(source),'-o',str(lib)],check=True,capture_output=True)
            client=root/'client.rs';client.write_text('extern crate fixture; fn main(){fixture::probe();}\n')
            for arm in ('baseline','candidate'):
                retained=b.retain_library(lib,root/'retained',arm)
                self.assertEqual(b.sha(retained),b.sha(lib))
                command=['rustc','--edition=2021',str(client),'--extern','fixture='+str(retained),'--emit=metadata','-o',str(root/(arm+'.rmeta'))]
                b.subprocess.run(command,check=True,capture_output=True)
                wrong=retained.parent/'baseline-libfixture.rlib';wrong.write_bytes(retained.read_bytes())
                bad_command=command.copy();bad_command[4]='fixture='+str(wrong)
                bad=b.subprocess.run(bad_command,capture_output=True,text=True)
                self.assertNotEqual(bad.returncode,0)
                self.assertIn('file name should be lib*.rlib',bad.stderr)

    def test_tracked_c_sources_and_separate_generated_compile_binding(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d).resolve()/'source';root.mkdir();(root/'src').mkdir();(root/'include').mkdir()
            for name in ('src/a.c','include/a.h','include/ta_config.h.cmake','VERSION','CMakeLists.txt'):
                (root/name).write_text('/* tracked */\n')
            (root/'.gitignore').write_text('include/ta_config.h\ninclude/unexpected.h\n')
            def git(*args):return b.subprocess.check_output(['git','-C',str(root),*args],text=True).strip()
            git('init','-q');git('add','.');git('-c','user.name=CI test','-c','user.email=test@example.invalid','commit','-qm','fixture');pin=git('rev-parse','HEAD')
            before=b.source_record(root,pin,True)
            header=root/'include/ta_config.h';header.write_text('/* generated */\n')
            self.assertEqual(before,b.source_record(root,pin,True))
            build=Path(d).resolve()/'build';build.mkdir();out=Path(d).resolve()/'out';out.mkdir()
            source=str(root/'src/a.c');dep=build/'a.c.o.d'
            dep.write_text('a.c.o: '+source+' '+str(header)+' '+str(root/'include/a.h')+'\n')
            command=build/'compile_commands.json';command.write_text(json.dumps([{'file':source,'directory':str(build),'command':'cc -o a.c.o -c '+source,'output':'a.c.o'}]))
            original_command=command.read_text()
            for output,cmd in [('a.c.o','cc -o wrong.o -c '+source),('../outside.o','cc -o ../outside.o -c '+source),('a.c.o','cc -c '+source),('a.c.o','cc -o a.c.o -o a.c.o -c '+source)]:
                command.write_text(json.dumps([{'file':source,'directory':str(build),'command':cmd,'output':output}]))
                with self.assertRaises(ValueError):b.c_generated_record(root,build,out,True if not(out/'c-generated').exists() else False)
            command.write_text(original_command)
            (out/'c-generated').rmdir()
            record=b.c_generated_record(root,build,out,True)
            self.assertEqual(record,b.c_generated_record(root,build,out));self.assertEqual(record['configured_header_consumers'],[source]);self.assertEqual(len(record['retained_files']),3)
            for path in (header,dep,command,root/'include/a.h',Path(next(iter(record['retained_files'])))):
                old=path.read_bytes();path.write_bytes(old+b'changed')
                with self.subTest(path=path):
                    try:changed=b.c_generated_record(root,build,out)
                    except (ValueError,json.JSONDecodeError):pass
                    else:self.assertNotEqual(record,changed)
                path.write_bytes(old)
            (root/'include/unexpected.h').write_text('bad')
            with self.assertRaisesRegex(ValueError,'unexpected generated'):b.source_record(root,pin,True)
            (root/'include/unexpected.h').unlink();dep.write_text('a.c.o: '+source+'\n')
            # Configuration is still retained when the compiler does not use it.
            import shutil
            shutil.rmtree(out/'c-generated')
            self.assertEqual(b.c_generated_record(root,build,out,True)['configured_header_consumers'],[])
            for bad in ('other.o: '+source+'\n','a.c.o: '+str(header)+'\n','a.c.o: '+source+' '+str(root/'include/unexpected.h')+'\n'):
                dep.write_text(bad)
                with self.assertRaises(ValueError):b.c_generated_record(root,build,out)

    def test_inventory_and_balance(self):
        self.assertEqual(len(b.CASES),15);self.assertEqual(len(set(b.CASES)),15);self.assertEqual(b.MODES,('typed',))
        self.assertEqual(len(b.ORDERS),12);self.assertEqual(set(collections.Counter(b.ORDERS).values()),{2})
        for arm in b.ARMS:self.assertEqual(collections.Counter(o.index(arm)for o in b.ORDERS),{0:4,1:4,2:4})
        self.assertEqual(15*3*12,540);self.assertEqual(540*31,16740)
        self.assertEqual(b.ORIGINAL,'62021c1d14ef5499505af5547384cab509adf3fc');self.assertEqual(b.BASELINE,'ccd3172940ed1d9daa4e7197f2265810852e8910')

    def test_json_and_types(self):
        for text in ['{"a":1,"a":2}','{"a":NaN}']:
            with self.assertRaises(ValueError):b.read_json(text)
        self.assertFalse(b.exact({'x':True},{'x':1}))

    def test_stdout_rejects_identity_sample_or_coverage_drift(self):
        sel=('sarext','default',100,'typed')
        for arm in b.ARMS:
            for timed in (False,True):b.parse(output(sel,arm,timed),sel,arm,timed)
        text=output(sel,'baseline',True)
        for bad in [text.splitlines()[1],text+'\n'+text,text.replace('"typed"','"abstract"'),text.replace('"n": 100','"n": true'),text.replace('"warmups": 5','"warmups": 4'),text.replace('"hardware_fma": false','"hardware_fma": 0')]:
            with self.subTest(bad=bad),self.assertRaises(ValueError):b.parse(bad,sel,'baseline',True)
        for samples in ([1]*30,[1]*30+[0],[1]*30+[True],[1]*30+[float('inf')]):
            lines=text.splitlines();row=json.loads(lines[1]);row['samples_ns']=samples
            with self.assertRaises(ValueError):b.parse(lines[0]+'\n'+json.dumps(row),sel,'baseline',True)
        row=json.loads(output(sel,'baseline',False));row['parameter_errors']=0
        with self.assertRaises(ValueError):b.parse(json.dumps(row),sel,'baseline',False)

    def test_raw_capture_shape_tail_and_inventory(self):
        with tempfile.TemporaryDirectory()as d:
            p=Path(d)/'cap';good=full('sar',100);p.write_bytes(good)
            cap=b.capture(p,'sar',100,True);self.assertEqual(cap['records'],181);self.assertEqual(cap['selected'],record('sar',100))
            for bad in [good[:-1],good+b'x',b'X'+good[1:],good[:-8]+struct.pack('<Q',0x7ff8000000000000),good[:8]+struct.pack('<Q',65)+good[16:]]:
                p.write_bytes(bad)
                with self.assertRaises(ValueError):b.capture(p,'sar',100,True)

    def test_c_nan_written_policy_and_raw_tail(self):
        with tempfile.TemporaryDirectory()as d:
            a=Path(d)/'C';z=Path(d)/'native';base=bytearray(full('sar',100));at=(64*8+96)+32
            for x,y in [(0x3ff0000000000000,0x3ff0000000000001),(0,1<<63),(0x7ff0000000000000,0xfff0000000000000),(0x7ff8000000000123,0x3ff0000000000000)]:
                first=base.copy();second=base.copy();struct.pack_into('<Q',first,at,x);struct.pack_into('<Q',second,at,y);a.write_bytes(first);z.write_bytes(second)
                with self.assertRaises(ValueError):b.compare_c_written(a,z,'sar',100,('sar','default',100,'typed'))
            first=base.copy();second=base.copy();struct.pack_into('<Q',first,at,0x7ff8000000000123);struct.pack_into('<Q',second,at,0xfff8000000000456);a.write_bytes(first);z.write_bytes(second)
            changes=b.compare_c_written(a,z,'sar',100,('sar','default',100,'typed'));self.assertEqual(len(changes),1);self.assertEqual(changes[0]['out_index'],0)
            second[-8:]=struct.pack('<Q',0x7ff8000000000000);z.write_bytes(second)
            with self.assertRaises(ValueError):b.capture(z,'sar',100,True)
            with self.assertRaises(ValueError):b.compare_c_written(a,z,'sar',100,('sar','default',100,'typed'))

    def test_selected_command_exact(self):
        p={'arms':{'candidate':{'binary':'candidate'}},'inputs':{'default/100':{'path':'input'}}}
        self.assertEqual(b.child_command(p,'candidate',('sar','default',100,'typed'),'out','golden'),['candidate','sar','default','typed','100','1000','input','out','--golden','golden'])

    def fake_execute(self,cmd,stem,timeout):
        arm=cmd[0];sel=(cmd[1],cmd[2],int(cmd[4]),cmd[3]);timed=cmd[8]=='--golden';self.events.append((timed,arm,sel));Path(cmd[7]).write_bytes(b'selected');return output(sel,arm,timed),{'minor':0,'major':0}

    def fake_capture(self,path,ind,n,full):return dict(sha256=b.sha(path),bytes=8,records=181 if full else 1,ranges=[],selected=b'selected')

    def fake_context(self,d):return types.SimpleNamespace(output=Path(d)),{'arms':{a:{'binary':a}for a in b.ARMS},'inputs':{f'{f}/{n}':{'path':'input'}for _,f,n in b.CASES}}

    def test_actual_controller_all45_preflights_before540_mock_children(self):
        with tempfile.TemporaryDirectory()as d:
            args,p=self.fake_context(d);self.events=[]
            with patch.object(b,'execute',self.fake_execute),patch.object(b,'capture',self.fake_capture),patch.object(b,'check_hits',return_value={}),patch.object(b,'compare_c_written',return_value=[]):
                v=b.prepare(args,p);r=b.measure(args,p,v)
            self.assertEqual(len(self.events),45+540);self.assertTrue(all(not x[0]for x in self.events[:45]));self.assertTrue(all(x[0]for x in self.events[45:]));self.assertEqual(r['children'],540);self.assertEqual(r['samples'],16740);self.assertEqual(len(r['results']),15)
            for k,case in enumerate(b.CASES):self.assertEqual([(a,c)for _,a,c in self.events[45+k*36:45+(k+1)*36]],[(a,(*case,'typed'))for order in b.ORDERS for a in order])

    def test_missing_gate_round_and_golden_fail_closed(self):
        with tempfile.TemporaryDirectory()as d:
            args,p=self.fake_context(d);self.events=[]
            with self.assertRaises(ValueError):b.measure(args,p,{'completed_before_any_timing':True,'checks':[]})
            with patch.object(b,'execute',self.fake_execute),patch.object(b,'capture',self.fake_capture),patch.object(b,'check_hits',return_value={}),patch.object(b,'compare_c_written',return_value=[]):v=b.prepare(args,p)
            Path(next(iter(v['goldens'].values()))['path']).write_bytes(b'bad')
            with self.assertRaisesRegex(ValueError,'golden changed'):b.measure(args,p,v)
        with self.assertRaises(ValueError):b.summarize([])

    def test_timeout_preserves_partial_logs(self):
        with tempfile.TemporaryDirectory()as d:
            stem=Path(d)/'timeout'
            with patch.object(b.subprocess,'run',side_effect=b.subprocess.TimeoutExpired(['x'],1,output=b'partial',stderr=b'why')),self.assertRaises(b.subprocess.TimeoutExpired):b.execute(['x'],stem,1)
            self.assertEqual(Path(str(stem)+'.stdout').read_text(),'partial');self.assertEqual(Path(str(stem)+'.stderr').read_text(),'why');self.assertTrue(Path(str(stem)+'-failure.json').exists())

    def test_every_negative_including_add_control_retained(self):
        rows=[{'key':'/'.join(map(str,(*c,'typed'))),'arm':a,'round':r,'samples_ns':[100+len(a)]*31}for c in b.CASES for r in range(1,13)for a in b.ARMS]
        results,negative=b.summarize(rows);self.assertEqual(len(results),15);self.assertTrue(any(x['is_add_control']for x in negative));self.assertEqual(sum(len(v)for v in results.values()),45)

    def test_source_static_manifest_is_exact_and_qualified(self):
        proof=Path(__file__).parent/'data/sarext-window-codegen';m=b.read_json((proof/'manifest.json').read_text());f=b.read_json((proof/'prefix-final-freeze.json').read_text());sources={'candidate':{'source_files':f}}
        with patch.object(b,'CANDIDATE',m['candidate_commit']):b.check_codegen_proof(proof,sources)
        bad={'candidate':{'source_files':dict(f)}};bad['candidate']['source_files'][next(iter(f))]='0'*64
        with patch.object(b,'CANDIDATE',m['candidate_commit']),self.assertRaises(ValueError):b.check_codegen_proof(proof,bad)

    def test_exact_source_footprint_and_add_control(self):
        keys=['ta_codegen/generator/src/backends/rust_window.rs','ta_codegen/generator/src/backends/rust_lang.rs','ta_codegen/output/rust/library/src/ta_func/sar.rs','ta_codegen/output/rust/library/src/ta_func/sarext.rs'];add='ta_codegen/output/rust/library/src/ta_func/add.rs'
        sources={a:{'source_files':{**{k:a for k in keys},add:'same'}}for a in ['baseline','candidate']};b.check_control_sources(sources);sources['candidate']['source_files'][add]='changed'
        with self.assertRaises(ValueError):b.check_control_sources(sources)


class CFG(unittest.TestCase):
    def rows(self,connected=False,stack=False,unknown=False):
        rows=[(0x100,'addsd','%xmm1, %xmm0'),(0x104,'movsd','%xmm0, 8(%rsp)'if stack else '%xmm0, (%rdi)'),(0x108,'call','*%rax'if unknown else '0x900 <fma@plt>'),(0x10c,'jne','0x100'),(0x110,'ret','')]
        if connected:rows.insert(3,(0x10a,'jae','0x120'))
        return rows+[(0x120,'call','*0x10(%rip) # 0x500'),(0x124,'ud2','')]

    def register_rows(self,reg='r15'):
        return [(0x80,'mov','0x12(%rip),%'+reg+' # 0x500'),(0x100,'addsd','%xmm1,%xmm0'),(0x104,'movsd','%xmm0,(%rdi)'),(0x108,'call','*%'+reg),(0x10c,'jne','0x100'),(0x110,'ret','')]

    def register_proven(self,rows,names=None,gots=None):
        return cg.cfg(rows,{0x900:'fma'} if names is None else names,{0x500:'fma'} if gots is None else gots)

    def test_register_fma_exact_load_and_repeated_known_c_calls(self):
        for reg in ('r12','r13','r14','r15'):
            r=self.register_proven(self.register_rows(reg));self.assertEqual(r['unknown_sites'],[]);self.assertEqual(r['fma_register_proof']['calls'],{'0x108':reg})
            rows=self.register_rows(reg);rows.insert(3,(0x106,'call','0x900 <fma>'))
            self.assertEqual(self.register_proven(rows)['unknown_sites'],[])

    def test_register_fma_missing_wrong_load_and_no_loop_bootstrap(self):
        for rows in (self.register_rows()[1:],[(0x70,'jmp','0x100'),*self.register_rows()]):
            self.assertIn('0x108',self.register_proven(rows)['unknown_sites'])
        for names,gots in (({}, {0x500:'fma'}),({0x900:'fma'},{0x500:'other'}),({0x900:'fma'},{})):
            self.assertIn('0x108',self.register_proven(self.register_rows(),names,gots)['unknown_sites'])
        # An unreachable load cannot seed its own disconnected loop.
        rows=[(0x70,'ret',''),*self.register_rows()]
        self.assertIn('0x108',self.register_proven(rows)['unknown_sites'])
        names=cg.function_names('1: 00000900 8 OBJECT LOCAL DEFAULT 1 fma\n2: 00000910 8 FUNC GLOBAL DEFAULT UND fma\n')
        self.assertEqual(names,{})

    def test_register_fma_overwrites_alias_reads_subregs_and_unknown_calls_kill(self):
        for op,args in [('mov','%rax,%r15'),('mov','%r15,%r14'),('test','%r15,%r15'),('xor','%r15d,%r15d'),('mov','%ax,%r15w'),('mov','%al,%r15b'),('cmovne','%rax,%r15'),('pop','%r15'),('call','0x901 <private_rust>'),('notrack','call *%rax')]:
            rows=self.register_rows();rows.insert(3,(0x106,op,args))
            with self.subTest(op=op,args=args):self.assertIn('0x108',self.register_proven(rows)['unknown_sites'])

    def test_register_fma_all_incoming_paths_must_be_known(self):
        for prelude in ([(0x70,'jne','0x100')],[(0x70,'jne','0x90')]):
            rows=[*prelude,*self.register_rows()[:1],(0x84,'jmp','0x100'),(0x90,'xor','%r15d,%r15d'),*self.register_rows()[1:]]
            self.assertIn('0x108',self.register_proven(rows)['unknown_sites'])
        # Both branches independently load the same resolved FMA pointer.
        rows=[(0x70,'jne','0x90'),*self.register_rows()[:1],(0x84,'jmp','0x100'),(0x90,'mov','0x12(%rip),%r15 # 0x500'),*self.register_rows()[1:]]
        self.assertEqual(self.register_proven(rows)['unknown_sites'],[])

    def test_output_cycle_and_disconnected_panic_not_whole_grep(self):
        r=cg.cfg(self.rows(),{}, {0x500:'core::panicking::panic_bounds_check'});loops=[g for g in r['cyclic_cfgs']if g['output_loop_candidate']];self.assertEqual(len(loops),1);self.assertFalse(loops[0]['bounds_panic_reachable']);self.assertFalse(loops[0]['unknown_exit_or_call_reachable'])

    def test_connected_panic_and_unknown_call_cannot_certify(self):
        for rows in [self.rows(connected=True),self.rows(unknown=True)]:
            r=cg.cfg(rows,{}, {0x500:'panic_bounds_check'});loop=next(g for g in r['cyclic_cfgs']if g['output_loop_candidate']);self.assertTrue(loop['bounds_panic_reachable']or loop['unknown_exit_or_call_reachable'])

    def test_nonoutput_fp_stack_loop_not_output_candidate(self):
        self.assertFalse(any(g['output_loop_candidate']for g in cg.cfg(self.rows(stack=True),{}, {})['cyclic_cfgs']))

    def test_partial_symbol_overlap_and_exec_bounds_fail(self):
        text='1: 00000100 64 FUNC LOCAL DEFAULT 1 sar_impl\n2: 00000120 8 FUNC LOCAL DEFAULT 1 other\n'
        with self.assertRaises(ValueError):cg.symbols(text,[(0x100,0x200)])
        with self.assertRaises(ValueError):cg.symbols('1: 00000100 64 FUNC LOCAL DEFAULT 1 sar_impl',[(0x110,0x200)])
        self.assertEqual(len(cg.symbols('1: 00000100 64 FUNC LOCAL DEFAULT 1 sar_impl\n2: 00000100 64 FUNC LOCAL DEFAULT 1 alias',[(0x100,0x200)])),1)

    def test_rela_got_and_import_binding(self):
        text='00000500 0008 R_X86_64_RELATIVE 00000900\n00000508 1234 R_X86_64_GLOB_DAT 00000000 fma@GLIBC_2.2.5 + 0'
        self.assertEqual(cg.relocs(text,{0x900:'panic_bounds_check'}),{0x500:'panic_bounds_check',0x508:'fma@GLIBC_2.2.5'})

    def test_instruction_scope_bytes_are_complete_and_bounded(self):
        good='100: f2 0f 58 c1 addsd %xmm1,%xmm0\n104: c3 ret\n200: cc int3'
        self.assertEqual(len(cg.parse_instructions(good,0x100,5)),2)
        for bad in ['104: c3 ret','100: c3 ret\n100: c3 ret',
                    '100: f2 0f 58 c1 addsd %xmm1,%xmm0',
                    '100: f2 0f 58 c1 addsd %xmm1,%xmm0\n105: c3 ret',
                    '100: (bad)', '100: c3 ret\n101: 00 (bad)']:
            with self.subTest(bad=bad),self.assertRaises(ValueError):cg.parse_instructions(bad,0x100,5)
        with self.assertRaises(ValueError):cg.parse_instructions(good,0x100,3)

    def test_scc_handles_long_function_without_recursion_limit(self):
        graph={n:[n+1]for n in range(3000)};graph[3000]=[0]
        self.assertEqual(cg.sccs(graph),[list(range(3001))])

    def test_tail_or_indirect_jump_cannot_certify(self):
        for op,args in [('jmp','*%rax'),('jmp','0x900'),('notrack','jmp *%rax')]:
            rows=self.rows();rows.insert(3,(0x10a,op,args))
            r=cg.cfg(rows,{},{})
            self.assertFalse(any(g['output_loop_candidate'] and not g['unknown_exit_or_call_reachable'] for g in r['cyclic_cfgs']))



if __name__=='__main__':unittest.main()
