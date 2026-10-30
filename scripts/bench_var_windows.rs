//! Frozen16-case matched public function-pointer route. Controller gates the enabled ELF before timing.
use std::{env,fs,hint::black_box,path::Path,time::Instant};
#[cfg(not(c_reference))]
use ta_lib::Core;
const POISON:u64=0x7ff8_0000_0000_55aa;
const TIMING_ENABLED:bool=true;
#[cfg(not(c_reference))]
type VarianceFn = fn(&Core,usize,usize,&[f64],i32,f64,&mut[f64])->Result<ta_lib::OutRange,ta_lib::RetCode>;
#[cfg(c_reference)]
type CVarianceFn = unsafe extern "C" fn(i32,i32,*const f64,i32,f64,*mut i32,*mut i32,*mut f64)->i32;
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
struct Case {kind:&'static str,api:&'static str,p:i32,n:usize,pattern:&'static str}
const CASES:[Case;16]=[
    Case { kind: "var", api: "typed", p: 2, n: 1000000, pattern: "wave" },
    Case { kind: "var", api: "typed", p: 5, n: 1000000, pattern: "wave" },
    Case { kind: "var", api: "typed", p: 200, n: 1000000, pattern: "wave" },
    Case { kind: "stddev", api: "typed", p: 2, n: 1000000, pattern: "wave" },
    Case { kind: "stddev", api: "typed", p: 5, n: 1000000, pattern: "wave" },
    Case { kind: "stddev", api: "typed", p: 200, n: 1000000, pattern: "wave" },
    Case { kind: "var", api: "typed", p: 5, n: 100, pattern: "wave" },
    Case { kind: "var", api: "typed", p: 5, n: 10000, pattern: "wave" },
    Case { kind: "stddev", api: "typed", p: 5, n: 100, pattern: "wave" },
    Case { kind: "stddev", api: "typed", p: 5, n: 10000, pattern: "wave" },
    Case { kind: "var", api: "abstract", p: 5, n: 1000000, pattern: "wave" },
    Case { kind: "stddev", api: "abstract", p: 5, n: 1000000, pattern: "wave" },
    Case { kind: "var", api: "typed", p: 5, n: 1000000, pattern: "flat" },
    Case { kind: "stddev", api: "typed", p: 5, n: 1000000, pattern: "highoffset" },
    Case { kind: "ema", api: "typed", p: 14, n: 1000000, pattern: "wave" },
    Case { kind: "add", api: "typed", p: 0, n: 1000000, pattern: "wave" },
];
impl Case {
 fn name(self)->String {format!("{}_{}_{}_{}_{}",self.kind,self.api,self.p,self.n,self.pattern)}
 fn iters(self)->usize {match self.n {100=>1000,10000=>10,1000000=>1,_=>panic!("rows")}}
 fn range(self)->(usize,usize) {let b=if self.kind=="add" {0}else{(self.p-1)as usize};(b,self.n-b)}
}
fn selected(name:&str)->Case {let mut found=CASES.into_iter().filter(|c|c.name()==name);let c=found.next().expect("unknown case");assert!(found.next().is_none());c}
#[cfg(c_reference)]
mod capi {
 use std::ffi::{c_char,c_void};
 extern "C" {
  pub fn TA_Initialize()->i32;
  pub fn TA_GetVersionString()->*const c_char;
  pub fn TA_VAR(s:i32,e:i32,x:*const f64,p:i32,d:f64,b:*mut i32,n:*mut i32,o:*mut f64)->i32;
  pub fn TA_STDDEV(s:i32,e:i32,x:*const f64,p:i32,d:f64,b:*mut i32,n:*mut i32,o:*mut f64)->i32;
  pub fn TA_EMA(s:i32,e:i32,x:*const f64,p:i32,b:*mut i32,n:*mut i32,o:*mut f64)->i32;
  pub fn TA_ADD(s:i32,e:i32,x:*const f64,y:*const f64,b:*mut i32,n:*mut i32,o:*mut f64)->i32;
  pub fn TA_GetFuncHandle(name:*const c_char,handle:*mut *const c_void)->i32;
  pub fn TA_ParamHolderAlloc(handle:*const c_void,holder:*mut *mut c_void)->i32;
  pub fn TA_ParamHolderFree(holder:*mut c_void)->i32;
  pub fn TA_SetInputParamRealPtr(holder:*mut c_void,i:u32,input:*const f64)->i32;
  pub fn TA_SetOptInputParamInteger(holder:*mut c_void,i:u32,value:i32)->i32;
  pub fn TA_SetOptInputParamReal(holder:*mut c_void,i:u32,value:f64)->i32;
  pub fn TA_SetOutputParamRealPtr(holder:*mut c_void,i:u32,output:*mut f64)->i32;
  pub fn TA_CallFunc(holder:*const c_void,s:i32,e:i32,b:*mut i32,n:*mut i32)->i32;
 }
}
#[cfg(not(c_reference))]
struct Engine(Core);
#[cfg(c_reference)]
struct Engine;
impl Engine {
 fn new()->Self {
  #[cfg(c_reference)] {assert_eq!(unsafe{capi::TA_Initialize()},0);Self}
  #[cfg(not(c_reference))] {Self(Core::new())}
 }
 fn batch(&self,c:Case,x:&[f64],second:&[f64],out:&mut[f64])->(i32,usize,usize) {
  assert_eq!(x.len(),c.n);assert_eq!(second.len(),c.n);assert_eq!(out.len(),c.n+8);assert!(c.n>0&&c.n<=1000000);
  #[cfg(c_reference)] {
   let(mut b,mut n)=(-321,-654);
   // Every raw input covers endIdx and the output includes the complete result plus canaries.
   let code=unsafe{if c.api=="abstract" {
    let name=if c.kind=="var" {b"VAR\0".as_slice()}else{b"STDDEV\0".as_slice()};
    let mut handle=std::ptr::null();let mut holder=std::ptr::null_mut();
    assert_eq!(capi::TA_GetFuncHandle(name.as_ptr().cast(),&mut handle),0);assert!(!handle.is_null());
    assert_eq!(capi::TA_ParamHolderAlloc(handle,&mut holder),0);assert!(!holder.is_null());
    assert_eq!(capi::TA_SetInputParamRealPtr(holder,0,x.as_ptr()),0);
    assert_eq!(capi::TA_SetOptInputParamInteger(holder,0,c.p),0);
    assert_eq!(capi::TA_SetOptInputParamReal(holder,1,1.0),0);
    assert_eq!(capi::TA_SetOutputParamRealPtr(holder,0,out.as_mut_ptr()),0);
    let code=capi::TA_CallFunc(holder,0,(c.n-1)as i32,&mut b,&mut n);
    assert_eq!(capi::TA_ParamHolderFree(holder),0);code
   }else{match c.kind {
    "var"=>black_box(capi::TA_VAR as CVarianceFn)(0,(c.n-1)as i32,x.as_ptr(),c.p,1.0,&mut b,&mut n,out.as_mut_ptr()),
    "stddev"=>black_box(capi::TA_STDDEV as CVarianceFn)(0,(c.n-1)as i32,x.as_ptr(),c.p,1.0,&mut b,&mut n,out.as_mut_ptr()),
    "ema"=>capi::TA_EMA(0,(c.n-1)as i32,x.as_ptr(),c.p,&mut b,&mut n,out.as_mut_ptr()),
    "add"=>capi::TA_ADD(0,(c.n-1)as i32,x.as_ptr(),second.as_ptr(),&mut b,&mut n,out.as_mut_ptr()),
    _=>panic!("kind")
   }}};assert!(b>=0&&n>=0);(code,b as usize,n as usize)
  }
  #[cfg(not(c_reference))] {
   let result=if c.api=="abstract" {
    let mut holder=ta_lib::abstract_api::get_func_handle(if c.kind=="var" {"VAR"}else{"STDDEV"}).unwrap().new_call(&self.0);
    holder.set_input(0,x).unwrap();holder.set_opt_input(0,c.p).unwrap();holder.set_opt_input(1,1.0).unwrap();holder.set_output(0,out).unwrap();holder.call(0,c.n-1)
   }else{match c.kind {
    // Public function pointers keep the actual ordinary typed Core body on the measured route.
    // The matched C calls also use black-box function pointers; no product annotations are changed.
    "var"=>black_box(Core::var as VarianceFn)(&self.0,0,c.n-1,x,c.p,1.0,out),
    "stddev"=>black_box(Core::stddev as VarianceFn)(&self.0,0,c.n-1,x,c.p,1.0,out),
    "ema"=>self.0.ema(0,c.n-1,x,c.p,out),
    "add"=>self.0.add(0,c.n-1,x,second,out),
    _=>panic!("kind")
   }};
   match result {Ok(r)=>(0,r.beg_idx,r.count),Err(e)=>(e.as_c_int(),0,0)}
  }
 }
}
fn load(path:&Path,c:Case)->(Vec<f64>,Vec<f64>) {
 let bytes=fs::read(path).unwrap();assert_eq!(bytes.len(),16+16*c.n);assert_eq!(&bytes[..8],b"VARFIX01");assert_eq!(u64::from_le_bytes(bytes[8..16].try_into().unwrap())as usize,c.n);
 let values:Vec<_>=bytes[16..].chunks_exact(8).map(|b|f64::from_bits(u64::from_le_bytes(b.try_into().unwrap()))).collect();
 assert!(values.iter().all(|v|v.is_finite()));(values[..c.n].to_vec(),values[c.n..].to_vec())
}
fn capture(c:Case,r:(i32,usize,usize),out:&[f64])->Vec<u8> {
 assert_eq!(r,(0,c.range().0,c.range().1));assert_eq!(out.len(),c.n+8);assert!(out[r.2..].iter().all(|v|v.to_bits()==POISON));assert!(out[..r.2].iter().all(|v|v.is_finite()));
 let mut bytes=b"VAROUT01".to_vec();for v in [c.n,r.1,r.2]{bytes.extend((v as u64).to_le_bytes())}for v in out {bytes.extend(v.to_bits().to_le_bytes())}bytes
}
fn sample(engine:&Engine,c:Case,x:&[f64],second:&[f64],out:&mut[f64])->(u128,(i32,usize,usize)) {
 assert!(TIMING_ENABLED,"Timer body not compiled");
 out.fill(f64::from_bits(POISON));let mut r=(0,0,0);let start=Instant::now();
 for _ in 0..c.iters(){r=engine.batch(c,black_box(x),black_box(second),black_box(out));black_box(&r);}
 (start.elapsed().as_nanos(),r)
}
type SampleFn = fn(&Engine,Case,&[f64],&[f64],&mut[f64])->(u128,(i32,usize,usize));
fn main() {
 let a:Vec<_>=env::args().collect();if a.len()==2&&a[1]=="--describe" {
  #[cfg(c_reference)] let version=unsafe{std::ffi::CStr::from_ptr(capi::TA_GetVersionString())}.to_str().unwrap();
  #[cfg(not(c_reference))] let version="Rust public Core and official ParamHolder";
  println!("{{\"version\":{:?},\"c_reference\":{},\"cases\":16,\"opaque_fnptr\":true,\"pointer_bytes\":{},\"timing_enabled\":{}}}",version,cfg!(c_reference),std::mem::size_of::<usize>(),TIMING_ENABLED);return
 }
 assert!(a.len()==5||a.len()==6,"case input output --capture-only | --golden path");let c=selected(&a[1]);let(x,second)=load(Path::new(&a[2]),c);let engine=Engine::new();let mut out=vec![f64::from_bits(POISON);c.n+8];let r=engine.batch(c,&x,&second,&mut out);let before=capture(c,r,&out);
 if a.len()==5 {assert_eq!(a[4],"--capture-only");fs::write(&a[3],before).unwrap();return}
 assert_eq!(a[4],"--golden");assert!(TIMING_ENABLED,"Timer body not compiled");let golden=fs::read(&a[5]).unwrap();assert_eq!(before,golden);
 for _ in 0..5 {let invoke=black_box(sample as SampleFn);black_box(invoke(&engine,c,&x,&second,&mut out));}
 let mut times=Vec::new();let mut last=r;for _ in 0..31 {let invoke=black_box(sample as SampleFn);let(ns,result)=invoke(&engine,c,&x,&second,&mut out);times.push(ns as f64/1000000.0);last=result;}
 let final_bytes=capture(c,last,&out);assert_eq!(final_bytes,golden);fs::write(&a[3],final_bytes).unwrap();println!("{{\"case\":{:?},\"n\":{},\"iterations\":{},\"repeats\":31,\"warmups\":5,\"checked_values\":{},\"samples_ms\":{:?}}}",c.name(),c.n,c.iters(),c.range().1,times);
}
#[cfg(test)] mod tests {
 use super::*;
 #[test] fn fixed_scope(){let names:std::collections::HashSet<_>=CASES.into_iter().map(Case::name).collect();assert_eq!(names.len(),16);for c in CASES{assert!(c.range().1>0);assert_eq!(c.n*c.iters(),if c.n==1000000{1000000}else{100000});}}
 #[test] fn timer_body_compiled(){assert!(TIMING_ENABLED);}
 #[test] fn explicit_function_pointer_types(){
  let timer=black_box(sample as SampleFn);assert_eq!(std::mem::size_of_val(&timer),std::mem::size_of::<usize>());
  #[cfg(not(c_reference))] {
   let incoming=black_box(Core::var as VarianceFn);let deviation=black_box(Core::stddev as VarianceFn);
   assert_eq!(std::mem::size_of_val(&incoming),std::mem::size_of::<usize>());assert_eq!(std::mem::size_of_val(&deviation),std::mem::size_of::<usize>());
  }
  #[cfg(c_reference)] {
   let incoming=black_box(capi::TA_VAR as CVarianceFn);let deviation=black_box(capi::TA_STDDEV as CVarianceFn);
   assert_eq!(std::mem::size_of_val(&incoming),std::mem::size_of::<usize>());assert_eq!(std::mem::size_of_val(&deviation),std::mem::size_of::<usize>());
  }
 }
 #[test] #[should_panic(expected="unknown case")]fn unknown(){selected("var_typed_14_1000000_wave");}
 #[test] #[should_panic]fn changed_tail(){let c=CASES[0];let out=vec![0.0;c.n+8];capture(c,(0,c.range().0,c.range().1),&out);}
}
