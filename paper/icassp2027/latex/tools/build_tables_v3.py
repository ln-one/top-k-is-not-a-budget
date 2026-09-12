"""Refresh full-ranking cost/quality tables; temporal tables retain v2 sources."""
import csv
from pathlib import Path
H=Path(__file__).resolve().parents[1];R=H.parents[2];P=R/'results/paper-experiments-v3'
N={'msmarco-passage-trec-dl-2019':'TREC-DL 2019','msmarco-passage-trec-dl-2020':'TREC-DL 2020','nfcorpus':'NFCorpus','scifact':'SciFact','trec-covid':'TREC-COVID'}
def update(name,rows):
 f=H/'tables'/name;s=f.read_text();a=s.index('\\midrule')+len('\\midrule');b=s.index('\\bottomrule',a)
 f.write_text(s[:a]+'\n'+'\n'.join(' & '.join(row)+r' \\' for row in rows)+'\n'+s[b:])
with (P/'complete-top20-review.csv').open() as f:
 rows=list(csv.DictReader(f))
assert sum(int(x['n']) for x in rows)==770 and all(x['n']==x['completed'] for x in rows)
update('cost-v3.tex',[[N[x['dataset']],x['n']]+[f"{float(x[k]):.0f}" for k in ('median','p95','maximum')] for x in rows])
with (P/'quality-budget-summary.csv').open() as f:
 rows=[x for x in csv.DictReader(f) if float(x['target'])==.95]
assert all(float(x['baseline20_completion'])==1 and x['quality_lower']==x['quality_upper'] for x in rows)
update('quality-v3.tex',[[N[x['dataset']]]+[f"{100*float(x[k]):.2f}" for k in ('quality_lower','cost_saving_lower')] for x in rows])

with (P/'aggregate.csv').open() as f:
 rows=[x for x in csv.DictReader(f) if x['batch']=='1' and x['budget']=='2048']
lookup={(x['dataset'],x['policy']):x for x in rows}
update('yield-v2.tex',[[name]+[f"{float(lookup[ds,policy][key]):.2f}" for key in ('mean_k_lower','k20_lower') for policy in ('balanced','dibud')] for ds,name in N.items()])
