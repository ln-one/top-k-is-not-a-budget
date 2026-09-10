#!/usr/bin/env python3
"""Frozen-budget output-contract and scheduling factorial comparison."""
import csv, json, hashlib, argparse
from pathlib import Path
from collections import defaultdict
from statistics import mean
import numpy as np
from run_anytime_frontier_pilot import UnequalDepthCertificate, load_qrels, ndcg_at_10, recall_at_100

parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,default=Path('results/matched-budget-truncation'))
parser.add_argument('--manifest',type=Path,default=Path('results/anytime-five-datasets-chunk64/raw/anytime_frontier_manifest.json'))
parser.add_argument('--trace',type=Path,default=Path('results/anytime-five-datasets-chunk64/derived/anytime_frontier_per_query.csv'))
parser.add_argument('--data-root',type=Path,help='Root containing canonical-v1 contents (datasets/ and experiments/)')
args=parser.parse_args()
OUT=args.output; OUT.mkdir(parents=True,exist_ok=True)
SRC=args.manifest; TRACE=args.trace
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(name, rows):
 with (OUT/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
source=json.loads(SRC.read_text())
if args.data_root:
 for entry in source['sources']:
  entry['path']=str(args.data_root / (entry['relative_path'] if 'relative_path' in entry else entry['path'].split('canonical-v1/',1)[1]))
for s in source['sources']:assert sha(s['path'])==s['sha256'],s['path']
traces=defaultdict(dict)
for r in csv.DictReader(TRACE.open()):
 if r['policy'] in ('balanced','blocker'):traces[r['dataset'],r['query_id']][int(r['work_budget']),r['policy']]=r
rows=[]; checks=0
with (OUT/'outputs.jsonl').open('w') as idsout:
 for ds in source['datasets']:
  paths=[Path(s['path']) for s in source['sources'] if s.get('dataset')==ds or '/'+ds+'/' in s['path']]
  run=json.loads(next(p for p in paths if p.name=='run.json').read_text())
  qrels=load_qrels(next(p for p in paths if p.name=='qrels.tsv'))
  for path in paths:
   if '/queries/' not in str(path):continue
   d=json.loads(path.read_text());qid=str(d['queryId']); a=d['densePrefixPointIds'];b=d['sparsePositivePrefixPointIds']
   cert=UnequalDepthCertificate(a,b,first_exhausted=len(a)==int(run['documents']),second_exhausted=len(b)==int(run['documents']) or len(b)<max(run['parameters']['depths']))
   ext=dict(zip(a,d['densePrefixExternalIds'],strict=True));ext.update(zip(b,d['sparsePositivePrefixExternalIds'],strict=True))
   truth=d['full']['orderedPointIdsTop101'][:100];jud=qrels.get(qid,{})
   positive={x for x,v in jud.items() if v>0}
   for budget in sorted({k[0] for k in traces[ds,qid]}):
    configs=[('fixed_topL',min(len(a),budget//2),min(len(b),budget//2))]
    for pol in ('balanced','blocker'):
     old=traces[ds,qid][budget,pol];configs.append((pol,int(old['dense_depth']),int(old['sparse_depth'])))
    work=[]
    for pol,da,db in configs:
     state=cert.frontier(da,db);seen=state.seen_first|state.seen_second
     zero=[str(cert.identities[i]) for i in cert._top(state.lower,seen,100)]
     assert list(state.output)==truth[:state.certified_k]
     if pol!='fixed_topL':
      old=traces[ds,qid][budget,pol]
      assert state.certified_k==int(old['certified_k_cap100'])
      assert abs(ndcg_at_10([ext[x] for x in state.output],jud)-float(old['returned_ndcg_at10']))<1e-12
      assert abs(recall_at_100([ext[x] for x in state.output],jud)-float(old['returned_recall_at100']))<1e-12
      checks+=1;work.append(da+db)
     outputs={'zero':zero} if pol=='fixed_topL' else {'zero':zero,'cert':list(state.output)}
     for mode,order in outputs.items():
      method=pol+'_'+mode
      idsout.write(json.dumps(dict(dataset=ds,query_id=qid,budget=budget,method=method,ids=order))+'\n')
      for cap in (20,100):
       output=order[:cap];e=[ext[x] for x in output];ten=output[:10]
       matched=sum(x==y for x,y in zip(ten,truth[:10]));complete=len(ten)==10
       rows.append(dict(dataset=ds,query_id=qid,budget=budget,cap=cap,method=method,dense_depth=da,sparse_depth=db,actual_reads=da+db,candidates=state.seen_count,returned=len(output),empty=int(not output),has10=int(complete),exact10=int(complete and ten==truth[:10]),position_agreement10=matched/10,top10_set_same_order_diff=int(complete and set(ten)==set(truth[:10]) and ten!=truth[:10]),ndcg10=ndcg_at_10(e,jud),recall=len(set(e)&positive)/len(positive) if positive else 0.))
    assert len(set(work))==1, (ds,qid,budget,work)
  print('Finished',ds,flush=True)
write('per_query.csv',rows)
metrics=['actual_reads','returned','empty','has10','exact10','position_agreement10','top10_set_same_order_diff','ndcg10','recall']
groups=defaultdict(list)
for r in rows:groups[r['dataset'],r['budget'],r['cap'],r['method']].append(r)
agg=[]
for (ds,B,cap,m),rs in sorted(groups.items()):agg.append(dict(dataset=ds,budget=B,cap=cap,method=m,queries=len(rs),**{k:mean(r[k] for r in rs) for k in metrics}))
write('aggregate.csv',agg)
macro=[]
for B,cap,m in sorted({(r['budget'],r['cap'],r['method']) for r in agg}):
 rs=[r for r in agg if (r['budget'],r['cap'],r['method'])==(B,cap,m)]
 macro.append(dict(budget=B,cap=cap,method=m,**{k:mean(r[k] for r in rs) for k in metrics}))
write('macro.csv',macro)
lines=['# 同预算截断融合对照','', f'真实冻结排名回放：{len(source["datasets"])} 个集合/快照，{len(traces)} 个查询—集合/快照状态；集合/快照等权宏平均。沿用历史 offset=59、chunk=64。不是标准 offset=60 或真实延迟实验。fixed_topL 每通道 B/2，耗尽不重分；其他方法沿用已存轨迹。同轨迹的 zero/cert 只改变输出规则。短输出缺失位置在位置一致率中计零，避免把短前缀的正确性误写成完整 Top-10 交付。','']
for cap in (20,100):
 lines += [f'## 输出上限 {cap}', '', '|预算|方法|实际读取|输出数|nDCG@10|Recall@cap|完整精确Top10率|位置一致率@10|','|---:|---|---:|---:|---:|---:|---:|---:|']
 for r in macro:
  if r['cap']==cap:lines.append(f"|{r['budget']}|{r['method']}|{r['actual_reads']:.2f}|{r['returned']:.2f}|{r['ndcg10']:.5f}|{r['recall']:.5f}|{r['exact10']:.4f}|{r['position_agreement10']:.4f}|")
(OUT/'analysis.md').write_text('\n'.join(lines)+'\n')
(OUT/'manifest.json').write_text(json.dumps(dict(source_manifest=str(SRC),data_root=str(args.data_root) if args.data_root else None,source_manifest_sha256=sha(SRC),trace=str(TRACE),trace_sha256=sha(TRACE),script_sha256=sha(__file__),source_files_verified=len(source['sources']),old_certified_states_reproduced=checks,rows=len(rows),outputs={p.name:sha(p) for p in OUT.iterdir() if p.name!='manifest.json'}),indent=2)+'\n')
print('Rows',len(rows),'verified states',checks)
