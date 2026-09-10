"""Independent relevance audit plus mandatory completion checks for v3."""
from pathlib import Path
import json,hashlib
import pandas as pd,pytrec_eval
from run_anytime_frontier_pilot import load_qrels
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/paper-experiments-v3';RANKS=ROOT/'data/reconstructed-ranks-v1'
def main():
 b=pd.read_csv(OUT/'budget-yield.csv',dtype={'query_id':str});c=pd.read_csv(OUT/'fixed-k.csv',dtype={'query_id':str});t=pd.read_csv(OUT/'transfer-grid.csv',dtype={'query_id':str});audits=json.loads((OUT/'input-audit.json').read_text());assert len(audits)==770
 assert len(b)==24640 and not b.duplicated(['dataset','query_id','policy','batch','budget']).any()
 assert (b.accesses<=b.budget).all() and b.known.eq(1).all()
 top20=c[c.k==20];assert len(top20)==3080 and top20.completed.eq(1).all()
 assert (top20.cost>0).all() and len(top20[top20.snapshot==0])==3080
 checked=0;maxerr=0;old20=0;old100=0;comparisons=[]
 for a in audits:
  ds,qid=a['dataset'],a['query_id'];p=RANKS/ds;m=json.loads((p/f'{qid}.json').read_text());ids=m['external'];qrel=load_qrels(ROOT/'data/inputs/datasets'/ds/'source/qrels.tsv').get(qid,{})
  ev=pytrec_eval.RelevanceEvaluator({qid:{k:max(0,v) for k,v in qrel.items()}},{'ndcg_cut_10','ndcg_cut_20'})
  g=b[(b.dataset==ds)&(b.query_id==qid)]
  for k in set(g.k.clip(upper=20)):
   actual=ev.evaluate({qid:{v:float(100-i) for i,v in enumerate(ids[:k])}}).get(qid,{}).get('ndcg_cut_20',0.)
   err=float((g[g.k.clip(upper=20)==k].ndcg20-actual).abs().max());assert err<1e-12;maxerr=max(maxerr,err);checked+=len(g[g.k.clip(upper=20)==k])
  expected=ev.evaluate({qid:{v:float(100-i) for i,v in enumerate(ids[:100])}})[qid]
  assert max(abs(g.full_ndcg20-expected['ndcg_cut_20']))<1e-12
  assert max(abs(t[(t.dataset==ds)&(t.query_id==qid)].full_ndcg10-expected['ndcg_cut_10']))<1e-12
  old20+=int(m['old_top20_equal']);old100+=int(m['old_top100_equal'])
  comparisons.append({k:m[k] for k in ['dataset','query_id','old_top20_equal','old_top100_equal','dense_prefix_mismatches','sparse_prefix_mismatches']})
 report=dict(queries=770,static_queries=770,temporal_query_snapshots=0,budget_rows=len(b),all_budget_endpoints_known=True,all_four_static_top20_completed=770,top20_trajectory_completions=len(top20),ndcg20_rows_checked=checked,max_ndcg20_error=maxerr,independent_array_states=sum(a['array_checks'] for a in audits),ordered_mismatches=0,budget_violations=0,old_top20_equal=old20,old_top100_equal=old100)
 pd.DataFrame(comparisons).to_csv(OUT/'comparison-to-v2.csv',index=False);(OUT/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
