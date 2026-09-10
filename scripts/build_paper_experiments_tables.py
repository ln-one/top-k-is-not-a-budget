from pathlib import Path
import shutil
import pandas as pd
root=Path(__file__).resolve().parents[1];p=root/'results/paper-experiments-v2';paper=root/'paper/icassp2027';latex=paper/'latex'
backup=paper/'archive/pre-experiments-v2';backup.mkdir(parents=True,exist_ok=True)
for f in ['experiments-zh.md','experiments-evidence.md']:
 if (paper/f).exists() and not (backup/f).exists():shutil.copy2(paper/f,backup/f)
for f in ['experiments.tex','abstract.tex','conclusion.tex']:
 if not (backup/f).exists():shutil.copy2(latex/'sections'/f,backup/f)
ds=['msmarco-passage-trec-dl-2019','msmarco-passage-trec-dl-2020','nfcorpus','scifact','trec-covid'];names=['TREC-DL 2019','TREC-DL 2020','NFCorpus','SciFact','TREC-COVID']
a=pd.read_csv(p/'aggregate.csv');c=pd.read_csv(p/'cost-summary.csv');q=pd.read_csv(p/'quality-budget-summary.csv');t=pd.read_csv(p/'transfer-summary.csv')
def table(name,caption,label,header,rows,fmt):
 text='\\begin{table}[t]\n\\centering\n\\caption{'+caption+'}\n\\label{'+label+'}\n\\small\n\\setlength{\\tabcolsep}{3pt}\n\\begin{tabular}{'+fmt+'}\n\\toprule\n'+header+' \\\\\n\\midrule\n'+'\n'.join(' & '.join(r)+' \\\\' for r in rows)+'\n\\bottomrule\n\\end{tabular}\n\\end{table}\n'
 (latex/'tables'/name).write_text(text)
rows=[]
for d,n in zip(ds,names):
 x=c[(c.dataset==d)&(c.policy=='dibud')&(c.batch==1)&(c.k==20)].iloc[0]
 p95=f'{x.p95_lower:.0f}' if x.p95_lower==x.p95_upper else '$\\geq '+f'{x.p95_lower:.0f}'+'$'
 rows.append([n,f'{x["n"]:.0f}',f'{x.median_lower:.0f}',p95,f'{100*x.completion:.1f}'])
table('cost-v2.tex','Sorted accesses to exact Top-20 under unit SNRA. Completion is observed within the saved rankings and 10,000-access limit; unresolved P95 values are lower bounds.','tab:cost','Query set & $n$ & Median & P95 & Complete (\\%)',rows,'lrrrr')
rows=[]
for d,n in zip(ds,names):
 g=a[(a.dataset==d)&(a.batch==1)&(a.budget==2048)].set_index('policy');x=g.loc['dibud'];z=g.loc['balanced'];rows.append([n,f'{z.mean_k_lower:.2f}',f'{x.mean_k_lower:.2f}',f'{z.k20_lower:.2f}',f'{x.k20_lower:.2f}'])
table('yield-v2.tex','Mean certified output at $B=2048$. Both methods use unit accesses and the same certifier. All endpoints in this table are observed.','tab:yield','& \\multicolumn{2}{c}{Cap 100} & \\multicolumn{2}{c}{Cap 20} \\\\ Query set & Balanced & DiBud & Balanced & DiBud',rows,'lrrrr')
rows=[]
for d,n in zip(ds,names):
 x=q[(q.dataset==d)&(q.target==.95)].iloc[0];quality=f'{100*x.quality_lower:.2f}' if abs(x.quality_upper-x.quality_lower)<1e-10 else f'{100*x.quality_lower:.2f}--{100*x.quality_upper:.2f}'
 saving=f'{100*x.cost_saving_lower:.2f}' if x.baseline20_completion==1 else '$\\geq '+f'{100*x.cost_saving_lower:.2f}'+'$'
 rows.append([n,quality,saving,f'{100*x.at20:.1f}'])
table('quality-v2.tex','Held-out Top-20 comparison after selecting the smallest budget retaining 95\\% of reference mean nDCG@20 on calibration queries. Retention is a ratio of dataset means. Intervals and $\\geq$ reflect unobserved continuations, not confidence intervals.','tab:quality','Query set & Retained (\\%) & Fewer accesses (\\%) & Top20 (\\%)',rows,'lrrr')
rows=[]
for d,n in zip(ds,names):
 x=t[t.dataset==d].iloc[0];rows.append([n,f'{x.ndcg10:.4f}',f'{x.full_ndcg10:.4f}',f'{100*x.ordered20:.1f}'])
table('transfer-v2.tex','Five-fold query transfer of the depth selected by calibration nDCG@10. Agreement is exact ordered Top-20 agreement with full-list RRF, distinct from relevance quality.','tab:transfer','Query set & Frozen $L$ & Full RRF & Agreement (\\%)',rows,'lrrr')
