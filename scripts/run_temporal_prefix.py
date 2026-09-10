#!/usr/bin/env python3
"""Replay locked balanced/blocker policies on five existing COVID snapshots."""
import argparse,csv,json,hashlib
from pathlib import Path
from collections import defaultdict
from statistics import mean
from run_anytime_frontier_pilot import UnequalDepthCertificate,advance_trace,result_row,load_qrels
p=argparse.ArgumentParser();p.add_argument('--data-root',type=Path,required=True);p.add_argument('--output',type=Path,default=Path('results/temporal-prefix'));args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
budgets=(128,256,512,1024,2048,4096,8192,10000);rows=[];sources=[];cohorts=[]
def add(path,ds):sources.append(dict(path=str(path),relative_path=str(path.relative_to(args.data_root)),dataset=ds,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
for round_id in range(1,6):
 root=args.data_root/'experiments/target-validity/chronological-v1'/f'round-{round_id}';runpath=root/'run.json';run=json.loads(runpath.read_text());ds=run['dataset'];add(runpath,ds);qp=args.data_root/'datasets'/ds/'source/qrels.tsv';add(qp,ds);qrels=load_qrels(qp);cohort=set()
 for path in sorted((root/'queries').glob('*.json')):
  add(path,ds);d=json.loads(path.read_text());assert d['status']=='ok';qid=str(d['queryId']);cohort.add(qid);a=d['densePrefixPointIds'];b=d['sparsePositivePrefixPointIds'];cert=UnequalDepthCertificate(a,b,first_exhausted=len(a)==int(run['documents']),second_exhausted=len(b)==int(run['documents']) or len(b)<max(run['parameters']['depths']))
  mapping=dict(zip(a,d['densePrefixExternalIds'],strict=True));mapping.update(zip(b,d['sparsePositivePrefixExternalIds'],strict=True))
  for policy in ('balanced','blocker'):
   trace=advance_trace(cert,policy,budgets,64)
   for B,(da,db,state) in trace.items():
    rows.append(result_row(ds,qid,policy,B,da,db,state,mapping,d['full']['orderedPointIdsTop101'][:100],d['full']['orderedExternalIdsTop100'],qrels.get(qid,{})))
 cohorts.append(cohort);print('Finished',ds,len(cohort),flush=True)
assert len(cohorts[0])==30 and all(x==cohorts[0] for x in cohorts)
with (args.output/'trace.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
manifest=dict(datasets=[f'trec-covid-chrono-r{i}' for i in range(1,6)],sources=sources,workBudgets=budgets,chunk=64,rrf_offset=59,queries_per_snapshot=30,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),note='Existing same 30 queries at five snapshots. Not new independent queries; no policy fitting on these results. Rank caps are not exhaustion. Logical work only.')
(args.output/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
