from pathlib import Path
import subprocess,ctypes,json,numpy as np
r=Path(__file__).resolve().parents[1];p=r/'results/completion-extension-v1';repo=r.parent/'worktrees/target-validity-system'
s=subprocess.check_output(['git','show','70f4943:lib/segment/src/spaces/simple_neon.rs'],cwd=repo,text=True)
a=s.index('pub(crate) unsafe fn cosine_preprocess_neon');b=s.index('#[cfg(test)]',a)
s=s[a:b].replace('#[cfg(target_feature = "neon")]','')
rs='use std::arch::aarch64::*;\ntype DenseVector=Vec<f32>;type VectorElementType=f32;type ScoreType=f32;\nfn is_length_zero_or_normalized(l:f32)->bool {l<f32::EPSILON||(l-1.0).abs()<=1.0e-6}\n'+s+'\n#[unsafe(no_mangle)] pub unsafe extern "C" fn ref_dot(a:*const f32,b:*const f32)->f32 {unsafe {dot_similarity_neon(std::slice::from_raw_parts(a,384),std::slice::from_raw_parts(b,384))}}\n#[unsafe(no_mangle)] pub unsafe extern "C" fn ref_norm(a:*mut f32) {unsafe {let x=cosine_preprocess_neon(std::slice::from_raw_parts(a,384).to_vec());std::ptr::copy_nonoverlapping(x.as_ptr(),a,384);}}\n'
(p/'frozen_kernel_reference.rs').write_text(rs);subprocess.run(['/Users/ln1/.cargo/bin/rustc','--edition=2024','--crate-type=cdylib','-O',str(p/'frozen_kernel_reference.rs'),'-o',str(p/'frozen_kernel_reference.dylib')],check=True)
c=ctypes.CDLL(str(p/'kernels.dylib'));ref=ctypes.CDLL(str(p/'frozen_kernel_reference.dylib'));ref.ref_dot.restype=ctypes.c_float;ptr=lambda x:ctypes.c_void_p(x.ctypes.data)
rng=np.random.default_rng(206010);a=rng.normal(size=(128,384)).astype('f4');q=rng.normal(size=(32,384)).astype('f4');a[::2]/=np.linalg.norm(a[::2],axis=1)[:,None];aa=a.copy();qq=q.copy();c.normalize(ptr(a),len(a));c.normalize(ptr(q),len(q))
for row in aa:ref.ref_norm(ptr(row))
for row in qq:ref.ref_norm(ptr(row))
assert np.array_equal(a.view('u4'),aa.view('u4')) and np.array_equal(q.view('u4'),qq.view('u4'))
y=np.empty((len(a),len(q)),np.float32);c.dense(ptr(a),len(a),ptr(q),len(q),ptr(y));z=np.array([[ref.ref_dot(ptr(row),ptr(query)) for query in q] for row in a],np.float32);assert np.array_equal(y.view('u4'),z.view('u4'))
(p/'kernel-audit.json').write_text(json.dumps(dict(reference_commit='70f4943d9604cd2b5fe2df60e93521015d87fa74',normalized_vectors=160,dot_products=4096,bitwise_equal=True),indent=2));print('Rust reference and C reconstruction bitwise equal')
