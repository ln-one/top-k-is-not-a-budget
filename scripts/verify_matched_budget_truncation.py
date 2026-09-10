import csv,json,struct
from pathlib import Path
out=Path('results/matched-budget-truncation')
rows=list(csv.DictReader((out/'per_query.csv').open()))
idx={(r['dataset'],r['query_id'],int(r['budget']),r['method'],int(r['cap'])):r for r in rows}
source=json.loads(Path('results/anytime-five-datasets-chunk64/raw/anytime_frontier_manifest.json').read_text())
selected={}
for s in source['sources']:
 if '/queries/' in s['path']:
  ds=Path(s['path']).parents[1].name
  if ds not in selected:selected[ds]=json.loads(Path(s['path']).read_text())
f32=lambda x:struct.unpack('f',struct.pack('f',x))[0]
checks=0
for line in (out/'outputs.jsonl').open():
 rec=json.loads(line);ds=rec['dataset'];qid=rec['query_id'];m=rec['method'];B=rec['budget']
 if not m.endswith('_zero') or str(selected[ds]['queryId'])!=qid:continue
 d=selected[ds];r=idx[ds,qid,B,m,100];depths=[int(r['dense_depth']),int(r['sparse_depth'])]
 score={}
 for points,depth in zip([d['densePrefixPointIds'],d['sparsePositivePrefixPointIds']],depths):
  for rank,x in enumerate(points[:depth],1):score[x]=f32(score.get(x,0.)+f32(1/(59+rank)))
 expected=sorted(score,key=lambda x:(-score[x],int(x.replace('-',''),16)))[:100]
 assert rec['ids']==expected
 checks+=1
for r in rows:
 assert int(r['actual_reads'])<=int(r['budget'])
 assert int(r['returned'])<=int(r['cap'])
 for k in ('ndcg10','recall','exact10','position_agreement10'):assert 0<=float(r[k])<=1+1e-12
 for pol in ('balanced','blocker'):
  if r['method']==pol+'_cert':
   z=idx[r['dataset'],r['query_id'],int(r['budget']),pol+'_zero',int(r['cap'])]
   assert all(r[k]==z[k] for k in ('actual_reads','dense_depth','sparse_depth','candidates'))
print('Independent zero-fill checks:',checks,'; all row and matched-state invariants passed')
(out/'verification.json').write_text(json.dumps({'independent_zero_fill_checks':checks,'verified_rows':len(rows),'matched_state_invariants':True},indent=2)+'\n')
