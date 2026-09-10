#!/usr/bin/env python3
"""Compare legacy exponential-gain nDCG with trec_eval linear-gain nDCG."""
import argparse,csv,json,hashlib,importlib.metadata
from pathlib import Path
from collections import defaultdict
from statistics import mean
import pytrec_eval
from run_anytime_frontier_pilot import load_qrels
p=argparse.ArgumentParser();p.add_argument('--data-root',type=Path,required=True);p.add_argument('--input',type=Path,default=Path('results/matched-budget-truncation'));p.add_argument('--manifest',type=Path,default=Path('results/anytime-five-datasets-chunk64/raw/anytime_frontier_manifest.json'));p.add_argument('--output',type=Path,default=Path('results/metric-audit'));args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
source=json.loads(args.manifest.read_text());qrels={};ext={}
for e in source['sources']:
 path=args.data_root/(e['relative_path'] if 'relative_path' in e else e['path'].split('canonical-v1/',1)[1])
 assert hashlib.sha256(path.read_bytes()).hexdigest()==e['sha256']
 ds=e.get('dataset') or (path.parents[1].name if '/queries/' in str(path) else next(d for d in source['datasets'] if '/'+d+'/' in str(path)))
 if path.name=='qrels.tsv':qrels[ds]=load_qrels(path)
 if '/queries/' in str(path):
  d=json.loads(path.read_text());mapping=dict(zip(d['densePrefixPointIds'],d['densePrefixExternalIds'],strict=True));mapping.update(zip(d['sparsePositivePrefixPointIds'],d['sparsePositivePrefixExternalIds'],strict=True));ext[ds,str(d['queryId'])]=mapping
legacy={(r['dataset'],r['query_id'],r['budget'],r['method'],r['cap']):r for r in csv.DictReader((args.input/'per_query.csv').open())}
groups=defaultdict(dict)
for line in (args.input/'outputs.jsonl').open():
 d=json.loads(line);qid=d['query_id'];ids=[ext[d['dataset'],qid][x] for x in d['ids']];groups[d['dataset'],d['budget'],d['method']][qid]={x:float(len(ids)-i) for i,x in enumerate(ids)}
rows=[];maxerror=0; negative_labels=sum(v<0 for js in qrels.values() for j in js.values() for v in j.values()); changed_rows=0
for ds,jud in qrels.items():
 normal=pytrec_eval.RelevanceEvaluator(jud,{'ndcg_cut_10','recall_20','recall_100'})
 exp=pytrec_eval.RelevanceEvaluator({q:{x:2**max(v,0)-1 for x,v in js.items()} for q,js in jud.items()},{'ndcg_cut_10'})
 for (dataset,B,m),runs in groups.items():
  if ds!=dataset:continue
  standard=normal.evaluate(runs);exponential=exp.evaluate(runs)
  for q in runs:
   st=standard.get(q,{});ep=exponential.get(q,{}).get('ndcg_cut_10',0.)
   for cap in (20,100):
    old=legacy[ds,q,str(B),m,str(cap)];err=abs(ep-float(old['ndcg10']));re=abs(st.get('recall_'+str(cap),0.)-float(old['recall']));maxerror=max(maxerror,err,re);assert re<1e-12,(ds,q,B,m,re); changed_rows+=int(err>1e-12)
    rows.append(dict(dataset=ds,query_id=q,budget=B,method=m,cap=cap,ndcg10_linear=st.get('ndcg_cut_10',0.),ndcg10_exponential=ep,recall=st.get('recall_'+str(cap),0.)))
 print('Audited',ds,flush=True)
def write(name,rs):
 with (args.output/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
write('per_query.csv',rows);agg=[];g=defaultdict(list)
for r in rows:g[r['dataset'],r['budget'],r['method'],r['cap']].append(r)
for (ds,B,m,cap),rs in sorted(g.items()):agg.append(dict(dataset=ds,budget=B,method=m,cap=cap,**{k:mean(r[k] for r in rs) for k in ('ndcg10_linear','ndcg10_exponential','recall')}))
write('aggregate.csv',agg);macro=[]
for B,m,cap in sorted({(r['budget'],r['method'],r['cap']) for r in agg}):
 rs=[r for r in agg if (r['budget'],r['method'],r['cap'])==(B,m,cap)];macro.append(dict(budget=B,method=m,cap=cap,**{k:mean(r[k] for r in rs) for k in ('ndcg10_linear','ndcg10_exponential','recall')}))
write('macro.csv',macro)
report={'rows':len(rows),'negative_qrel_labels':negative_labels,'rows_changed_by_clamping_negative_labels':changed_rows,'max_absolute_reproduction_error':maxerror,'evaluator':'pytrec-eval-terrier','version':importlib.metadata.version('pytrec-eval-terrier'),'finding':'Historical nDCG uses exponential gains 2^rel-1; trec_eval default uses linear rel. Both exported separately. Historical Recall uses relevance >0. Negative judgment labels clamped to zero gain in external exponential evaluation; differences explicitly counted.','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'input_manifest_sha256':hashlib.sha256((args.input/'manifest.json').read_bytes()).hexdigest()}
(args.output/'audit.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
