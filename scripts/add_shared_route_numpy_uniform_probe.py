"""Fixed pre-data Linux NumPy uniform-mode probe; no product imports or timers."""
from pathlib import Path
import argparse,hashlib,json,platform,re,shutil,struct,sys
SIDES=('prior','combined','candidate','original')
MODE='numpy-2.5.3-linux-x86_64-unfused-uniform'
EXPECTED_WORDS=(
 '408ec2f5b5a2687a','408829b5743ebdef','4072b75a8023e527','405b30f5e4c0ec5f',
 '408b67a5d765fb2d','4078faa999e566cb','407f908ab9ecb3e2','406b023f1fa25d00',
 '40797e52a1f098ea','406f1e3972ff7afa','408c73bfbfc09b5e','40822fdbad3a7b14',
 '407a208d2b0ee4ea','40733a9a7e3b5c1e','408ac96b830061b6','40771b920a613bbb',
 '4080ee7cb227c5e2','408de08c741d9f27','407e35d54624d770','408a304de35f5f03',
 '406071c3bda086b3','407defeb1c0e6996','40841095b50256df','40809acbe72d3208',
 '4075b496cb25be18','4064d91265c34b00','407dbe2b7d54ec84','40826449b973e29a',
 '408d42b7bcb2f33f','407c048d722eda9a','408daade2a0ac081','4083617b665a1ff7')
def need(ok,message):
 if not ok:raise ValueError(message)
def file_sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def elf_header(header):
 need(len(header)==64 and header[:7]==b'\x7fELF\x02\x01\x01'and struct.unpack_from('<HHI',header,16)==(3,62,1)and struct.unpack_from('<H',header,52)[0]==64,'NumPy generator must be actual ELF64LE x86-64 ET_DYN')
def probe_record(side,module_dir):
 import numpy as np
 import numpy.random._generator as generator
 need(side in SIDES,'fixed probe arm')
 # A private Generator in this separate process; no fixture Generator is touched.
 rng=np.random.default_rng(260126);rng.normal(0,.1,1000);values=rng.uniform(100,1000,32)
 path=Path(generator.__file__).resolve();raw=path.read_bytes();destination=Path(module_dir)/path.name;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,destination)
 return {'side':side,'mode':MODE,'python_executable':str(Path(sys.executable).absolute()),'python':platform.python_version(),'system':platform.system(),'machine':platform.machine(),'byteorder':sys.byteorder,'numpy':np.__version__,'bit_generator':type(rng.bit_generator).__name__,'seed':260126,'normal_draws':1000,'normal_loc':0,'normal_scale':.1,'uniform_draws':32,'uniform_low':100,'uniform_high':1000,'words_u64_hex':[format(int(x),'016x')for x in values.view(np.uint64)],'generator_module':{'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'header64_hex':raw[:64].hex(),'retained_path':str(destination.absolute())}}
def validate_record(row,side,workspace):
 workspace=Path(workspace).resolve();module=row.get('generator_module',{})
 fixed={'side':side,'mode':MODE,'python_executable':str(workspace/'envs'/side/'bin/python'),'python':'3.12.15','system':'Linux','machine':'x86_64','byteorder':'little','numpy':'2.5.3','bit_generator':'PCG64','seed':260126,'normal_draws':1000,'normal_loc':0,'normal_scale':.1,'uniform_draws':32,'uniform_low':100,'uniform_high':1000,'words_u64_hex':list(EXPECTED_WORDS)}
 need(set(row)==set(fixed)|{'generator_module'},'exact uniform probe fields')
 for key,value in fixed.items():need(type(row[key])is type(value)and row[key]==value,'fixed uniform runtime/vector '+key)
 need(set(module)=={'path','sha256','bytes','header64_hex','retained_path'},'exact generator module fields');source=Path(module['path']);name=source.name
 need(re.fullmatch(r'_generator\.cpython-312-x86_64-linux-gnu\.so',name)is not None and source.parent==workspace/'envs'/side/'lib/python3.12/site-packages/numpy/random','actual arm NumPy generator module path')
 need(type(module['bytes'])is int and module['bytes']>=64 and re.fullmatch('[0-9a-f]{64}',module['sha256'])is not None,'actual generator module size/hash');need(module['retained_path']==str(workspace/'add-shared-route-results/uniform-native'/side/name),'actual retained generator arm path')
 need(type(module['header64_hex'])is str and re.fullmatch('[0-9a-f]{128}',module['header64_hex'])is not None,'generator header bytes');elf_header(bytes.fromhex(module['header64_hex']));return row

def validate_records(records,workspace):
 need(isinstance(records,dict)and list(records)==list(SIDES),'four probes in actual build-arm order')
 for side,row in records.items():validate_record(row,side,workspace)
 modules=[r['generator_module']for r in records.values()];need(len({(m['sha256'],m['bytes'],m['header64_hex'])for m in modules})==1,'identical NumPy generator bytes across arms');return {'mode':MODE,'arms':list(SIDES),'records':records}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--side',choices=SIDES,required=True);p.add_argument('--workspace',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--module-dir',type=Path,required=True);args=p.parse_args();row=probe_record(args.side,args.module_dir);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(row,indent=2)+'\n');validate_record(row,args.side,args.workspace)
if __name__=='__main__':main()
