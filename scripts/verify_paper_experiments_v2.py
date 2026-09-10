"""Independent metric and saved-state checks for the paper replay."""
import json
from pathlib import Path
import pandas as pd
import pytrec_eval
from run_anytime_frontier_pilot import load_qrels,UnequalDepthCertificate
OUT=Path('results/paper-experiments-v2')
def main():
 b=pd.read_csv(OUT/'budget-yield.csv',dtype={'query_id':str});audit=json.loads((OUT/'input-audit.json').read_text());maxerr=0.;checked=0;states=0
 for src in audit:
    ds=src['dataset'];qid=src['query_id'];data=json.loads(Path(src['path']).read_text());jud=load_qrels(Path('data/inputs/datasets')/ds/'source/qrels.tsv').get(qid,{})
    ids=data['full']['orderedExternalIdsTop100'];ev=pytrec_eval.RelevanceEvaluator({qid:{x:max(0,v) for x,v in jud.items()}},{'ndcg_cut_10','ndcg_cut_20'})
    qs=b[(b.dataset==ds)&(b.query_id==qid)]
    for k in set(min(20,int(k)) for k in qs.k):
      score=ev.evaluate({qid:{x:float(100-i) for i,x in enumerate(ids[:k])}}).get(qid,{}).get('ndcg_cut_20',0.)
      actual=qs[qs.k.clip(upper=20)==k].ndcg20.to_numpy();err=max(abs(actual-score));maxerr=max(maxerr,float(err));assert err<1e-12,(ds,qid,k,err);checked+=len(actual)
    # Independently audit each saved endpoint through the array certifier.
    cert=UnequalDepthCertificate(data['densePrefixPointIds'],data['sparsePositivePrefixPointIds'],first_exhausted=src['dense_exhausted'],second_exhausted=src['sparse_exhausted'])
    for (d,s),g in qs.groupby(['dense','sparse']):
      state=cert.frontier(int(d),int(s));assert state.certified_k==int(g.k.iloc[0]);assert list(state.output)==data['full']['orderedPointIdsTop101'][:state.certified_k];states+=1
    assert (qs.accesses<=qs.budget).all()
 report=dict(queries=len(audit),budget_rows=len(b),ndcg20_rows_checked=checked,max_ndcg20_error=maxerr,independent_array_endpoints=states,ordered_mismatches=0,budget_violations=0,smoke_array_checks=json.loads(Path('results/paper-experiments-v2-smoke/manifest.json').read_text())['array_checks'])
 (OUT/'verification.json').write_text(json.dumps(report,indent=2));print(report)
if __name__=='__main__':main()
