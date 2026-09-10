"""Build review tables from verified full Top-20 completions."""
from pathlib import Path
import json
import numpy as np,pandas as pd
O=Path('results/paper-experiments-v3');DS=['msmarco-passage-trec-dl-2019','msmarco-passage-trec-dl-2020','nfcorpus','scifact','trec-covid'];N=['TREC-DL 2019','TREC-DL 2020','NFCorpus','SciFact','TREC-COVID']
def main():
 v=json.loads((O/'verification.json').read_text());assert v['top20_trajectory_completions']==3080
 c=pd.read_csv(O/'fixed-k.csv',dtype={'query_id':str});z=c[(c.k==20)&(c.batch==1)&(c.policy=='dibud')];rows=[]
 for ds in DS:
  x=z[z.dataset==ds];assert x.completed.eq(1).all();values=x.cost.to_numpy();rows.append(dict(dataset=ds,n=len(x),completed=len(x),median=float(np.quantile(values,.5,method='inverted_cdf')),p95=float(np.quantile(values,.95,method='inverted_cdf')),p99=float(np.quantile(values,.99,method='inverted_cdf')),maximum=float(values.max()),mean=float(values.mean())))
 costs=pd.DataFrame(rows);costs.to_csv(O/'complete-top20-review.csv',index=False)
 a=pd.read_csv(O/'aggregate.csv');at=a[(a.dataset.isin(DS))&(a.batch==1)&(a.budget==2048)].groupby('policy').mean(numeric_only=True);bal=at.loc['balanced','mean_k_lower'];di=at.loc['dibud','mean_k_lower']
 q=pd.read_csv(O/'quality-budget-summary.csv');q=q[q.target==.95].set_index('dataset').loc[DS]
 # Preserve the slowest per-query interval as evidence, without hand-picking a favorable run.
 case=[]
 for ds in DS:
  for qid in z[z.dataset==ds].nlargest(3,'cost').query_id:
   x=c[(c.dataset==ds)&(c.query_id==qid)&(c.policy=='dibud')&(c.batch==1)&(c.k<=20)].sort_values('k');times=x.cost.to_numpy();gap=np.diff(np.r_[0,times]);i=int(gap.argmax());case.append(dict(dataset=ds,query_id=qid,from_k=i,to_k=i+1,from_accesses=float(times[i-1]) if i else 0,to_accesses=float(times[i]),gap=float(gap[i]),total=float(times[-1]),share=float(gap[i]/times[-1])))
 pd.DataFrame(case).to_csv(O/'long-tail-cases.csv',index=False)
 lines=['# 完整排名重跑：核验结果','','全部770条静态查询均完成精确 Top-20；两种调度、两种访问粒度共3080条轨迹，全部完成。时间快照部分缺失原始文件，本轮未重算，不混入静态完整成本结果。','','## 3.3 可用数据','','以下为逐条 DiBud 调度，单位是逻辑排名访问次数。所有值均为实际完成成本。','','| 查询集 | 查询数 | 中位数 | P95 | 最大值 |','|---|---:|---:|---:|---:|']
 for n,r in zip(N,rows):lines.append(f"| {n} | {r['n']} | {r['median']:,.0f} | {r['p95']:,.0f} | {r['maximum']:,.0f} |")
 lines+=['','## 同预算对照','',f'预算2048，前100位置内的集合等权平均认证数量：Balanced {bal:.4f}，DiBud {di:.4f}，相对变化 {(di/bal-1)*100:.2f}%。','','## 95%校准目标的留出表现','','| 查询集 | nDCG@20保留 | 访问节省 |','|---|---:|---:|']
 for n,(_,r) in zip(N,q.iterrows()):lines.append(f'| {n} | {r.quality_lower*100:.2f}% | {r.cost_saving_lower*100:.2f}% |')
 lines+=['','## 口径与验证','','采用统一重建排名，不拼接旧排名；原始向量与模型不变，Sparse 使用固定的原始词项顺序进行float32累加。旧实验v2保留，新结果v3独立存放。',f"独立数组认证器核对 {v['independent_array_states']:,} 个记录状态；pytrec_eval 核对 {v['ndcg20_rows_checked']:,} 条预算记录，最大误差 {v['max_ndcg20_error']:.3g}。未出现错误前缀或超预算访问。",f"与旧参考的有序Top-20一致：{v['old_top20_equal']}/770；有序Top-100一致：{v['old_top100_equal']}/770。评价均以本轮完整融合为参考。",'','这里只保证Top-20基线完成；不声称所有Top-50或Top-100基线已跑至完成。读取工作量不是端到端时延。']
 (O/'RESULTS-REVIEW.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))
if __name__=='__main__':main()
