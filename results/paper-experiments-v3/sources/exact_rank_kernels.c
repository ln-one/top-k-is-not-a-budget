// Replay the frozen ARM64 Qdrant float32 arithmetic, without fast-math.
// Source: Qdrant commit 70f4943, spaces/simple_neon.rs and posting_batch.rs.
#include <arm_neon.h>
#include <math.h>
#include <stdint.h>
static float dot(const float *a,const float *b) {
 float32x4_t s1=vdupq_n_f32(0),s2=s1,s3=s1,s4=s1;
 for(int i=0;i<384;i+=16){s1=vfmaq_f32(s1,vld1q_f32(a+i),vld1q_f32(b+i));s2=vfmaq_f32(s2,vld1q_f32(a+i+4),vld1q_f32(b+i+4));s3=vfmaq_f32(s3,vld1q_f32(a+i+8),vld1q_f32(b+i+8));s4=vfmaq_f32(s4,vld1q_f32(a+i+12),vld1q_f32(b+i+12));}
 return ((vaddvq_f32(s1)+vaddvq_f32(s2))+vaddvq_f32(s3))+vaddvq_f32(s4);
}
void normalize(float *a,int n){for(int j=0;j<n;j++,a+=384){float32x4_t s1=vdupq_n_f32(0),s2=s1,s3=s1,s4=s1;for(int i=0;i<384;i+=16){float32x4_t v=vld1q_f32(a+i);s1=vfmaq_f32(s1,v,v);v=vld1q_f32(a+i+4);s2=vfmaq_f32(s2,v,v);v=vld1q_f32(a+i+8);s3=vfmaq_f32(s3,v,v);v=vld1q_f32(a+i+12);s4=vfmaq_f32(s4,v,v);}float len=vaddvq_f32(vaddq_f32(vaddq_f32(s1,s2),vaddq_f32(s3,s4)));if(len<1.1920929e-7f||fabsf(len-1.0f)<=1.e-6f)continue;float inv=1.0f/sqrtf(len);for(int i=0;i<384;i++)a[i]*=inv;}}
void dense(const float *a,int n,const float *q,int nq,float *out){for(int i=0;i<n;i++)for(int j=0;j<nq;j++)out[i*nq+j]=dot(q+384*j,a+384*i);}
void sparse(const int32_t *offset,const int32_t *ids,const float *vals,int n,const int32_t *qo,const int32_t *qi,const float *qv,int nq,float *out){for(int d=0;d<n;d++)for(int q=0;q<nq;q++){int i=offset[d],end=offset[d+1],j=qo[q];float s=0;while(i<end&&j<qo[q+1]){if(ids[i]<qi[j])i++;else if(ids[i]>qi[j])j++;else{s+=vals[i]*qv[j];i++;j++;}}out[d*nq+q]=s;}}
