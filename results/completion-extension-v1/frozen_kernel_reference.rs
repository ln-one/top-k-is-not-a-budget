use std::arch::aarch64::*;
type DenseVector=Vec<f32>;type VectorElementType=f32;type ScoreType=f32;
fn is_length_zero_or_normalized(l:f32)->bool {l<f32::EPSILON||(l-1.0).abs()<=1.0e-6}
pub(crate) unsafe fn cosine_preprocess_neon(mut vector: DenseVector) -> DenseVector {
    unsafe {
        let n = vector.len();
        let m = n - (n % 16);
        let mut ptr: *const f32 = vector.as_ptr();
        let mut sum1 = vdupq_n_f32(0.);
        let mut sum2 = vdupq_n_f32(0.);
        let mut sum3 = vdupq_n_f32(0.);
        let mut sum4 = vdupq_n_f32(0.);

        let mut i: usize = 0;
        while i < m {
            let d1 = vld1q_f32(ptr);
            sum1 = vfmaq_f32(sum1, d1, d1);

            let d2 = vld1q_f32(ptr.add(4));
            sum2 = vfmaq_f32(sum2, d2, d2);

            let d3 = vld1q_f32(ptr.add(8));
            sum3 = vfmaq_f32(sum3, d3, d3);

            let d4 = vld1q_f32(ptr.add(12));
            sum4 = vfmaq_f32(sum4, d4, d4);

            ptr = ptr.add(16);
            i += 16;
        }

        let mut length = vaddvq_f32(vaddq_f32(vaddq_f32(sum1, sum2), vaddq_f32(sum3, sum4)));

        for v in vector.iter().take(n).skip(m) {
            length += v.powi(2);
        }
        if is_length_zero_or_normalized(length) {
            return vector;
        }

        let inv_length = 1.0 / length.sqrt();
        let v_inv_length = vdupq_n_f32(inv_length);
        let mut_ptr: *mut f32 = vector.as_mut_ptr();

        let mut i: usize = 0;

        while i + 15 < n {
            let v1 = vld1q_f32(mut_ptr.add(i));
            let v2 = vld1q_f32(mut_ptr.add(i + 4));
            let v3 = vld1q_f32(mut_ptr.add(i + 8));
            let v4 = vld1q_f32(mut_ptr.add(i + 12));
            vst1q_f32(mut_ptr.add(i), vmulq_f32(v1, v_inv_length));
            vst1q_f32(mut_ptr.add(i + 4), vmulq_f32(v2, v_inv_length));
            vst1q_f32(mut_ptr.add(i + 8), vmulq_f32(v3, v_inv_length));
            vst1q_f32(mut_ptr.add(i + 12), vmulq_f32(v4, v_inv_length));
            i += 16;
        }

        while i + 3 < n {
            let v = vld1q_f32(mut_ptr.add(i));
            vst1q_f32(mut_ptr.add(i), vmulq_f32(v, v_inv_length));
            i += 4;
        }

        for v in vector.iter_mut().take(n).skip(i) {
            *v *= inv_length;
        }

        vector
    }
}


pub(crate) unsafe fn dot_similarity_neon(
    v1: &[VectorElementType],
    v2: &[VectorElementType],
) -> ScoreType {
    unsafe {
        let n = v1.len();
        let m = n - (n % 16);
        let mut ptr1: *const f32 = v1.as_ptr();
        let mut ptr2: *const f32 = v2.as_ptr();
        let mut sum1 = vdupq_n_f32(0.);
        let mut sum2 = vdupq_n_f32(0.);
        let mut sum3 = vdupq_n_f32(0.);
        let mut sum4 = vdupq_n_f32(0.);

        let mut i: usize = 0;
        while i < m {
            sum1 = vfmaq_f32(sum1, vld1q_f32(ptr1), vld1q_f32(ptr2));
            sum2 = vfmaq_f32(sum2, vld1q_f32(ptr1.add(4)), vld1q_f32(ptr2.add(4)));
            sum3 = vfmaq_f32(sum3, vld1q_f32(ptr1.add(8)), vld1q_f32(ptr2.add(8)));
            sum4 = vfmaq_f32(sum4, vld1q_f32(ptr1.add(12)), vld1q_f32(ptr2.add(12)));
            ptr1 = ptr1.add(16);
            ptr2 = ptr2.add(16);
            i += 16;
        }
        let mut result = vaddvq_f32(sum1) + vaddvq_f32(sum2) + vaddvq_f32(sum3) + vaddvq_f32(sum4);
        for i in 0..n - m {
            result += (*ptr1.add(i)) * (*ptr2.add(i));
        }
        result
    }
}


#[unsafe(no_mangle)] pub unsafe extern "C" fn ref_dot(a:*const f32,b:*const f32)->f32 {unsafe {dot_similarity_neon(std::slice::from_raw_parts(a,384),std::slice::from_raw_parts(b,384))}}
#[unsafe(no_mangle)] pub unsafe extern "C" fn ref_norm(a:*mut f32) {unsafe {let x=cosine_preprocess_neon(std::slice::from_raw_parts(a,384).to_vec());std::ptr::copy_nonoverlapping(x.as_ptr(),a,384);}}
