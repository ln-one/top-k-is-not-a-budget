"""Complete Top-20 on reconstructed full rankings; never splice old prefixes.
Outputs are provisional until source-order equivalence is established.
"""
import sys,json,time,hashlib
from pathlib import Path
import numpy as np,pandas as pd
from pilot_grouped_frontier import GroupedFrontier
from run_paper_experiments_v2 import preferred
from run_anytime_frontier_pilot import position_score,UnequalDepthCertificate
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/completion-extension-v1';ds=sys.argv[1]
p=OUT/ds;qids=json.loads((p/'queries.json').read_text());uu=np.load(p/'uuids.npy',mmap_mode='r')
records={}
for f in (ROOT/'data/inputs/experiments/target-validity/static-v3'/ds/'queries').glob('*.json'):
 d=json.loads(f.read_text());records[str(d['queryId'])]=d
class Stream:
 def __init__(self,order): self.order=order
 def __len__(self):return len(self.order)
 def __getitem__(self,i):
  if isinstance(i,slice):return uu[self.order[i]].tolist()
  return str(uu[self.order[i]])
rows=[]
for qid in qids:
 done=p/f'{qid}-completion.json'
 if done.exists():rows.append(json.loads(done.read_text()));continue
 start=time.time();da=np.load(p/f'{qid}-dense-order.npy',mmap_mode='r');sa=np.load(p/f'{qid}-sparse-order.npy',mmap_mode='r');a,b=Stream(da),Stream(sa)
 scores=np.zeros(len(uu),np.float32);scores[da]=position_score(np.arange(1,len(da)+1));scores[sa]+=position_score(np.arange(1,len(sa)+1))
 top=np.argpartition(scores,-101)[-101:];cut=scores[top].min();top=np.flatnonzero(scores>=cut);top=top[np.lexsort((uu[top],-scores[top]))][:101];full=uu[top].tolist();old=records[qid]
 c=GroupedFrontier(a,b,(True,True));c.frontier();times={};events=[];checks=0
 while len(c.output)<20:
  ch=preferred(c,'dibud',0,1)
  if ch is None:raise RuntimeError('Exhausted before Top20')
  before=len(c.output);c.read(ch,1);c.frontier()
  if len(c.output)>before:
   assert c.output==full[:len(c.output)],(qid,'wrong prefix')
   for k in range(before+1,min(20,len(c.output))+1):times[k]=sum(c.depth)
   events.append(dict(accesses=sum(c.depth),dense=c.depth[0],sparse=c.depth[1],k=len(c.output)))
  if sum(c.depth)%100000==0:print(ds,qid,'reads',sum(c.depth),'k',len(c.output),flush=True)
 # Independent array certification at all emission endpoints. Respect known exhaustion only at actual ends.
 ref=UnequalDepthCertificate(a[:c.depth[0]],b[:c.depth[1]],first_exhausted=c.depth[0]==len(a),second_exhausted=c.depth[1]==len(b))
 for e in events:
  z=ref.frontier(e['dense'],e['sparse']);assert z.output==tuple(full[:e['k']]);checks+=1
 row=dict(dataset=ds,query_id=qid,cost20=times[20],dense=c.depth[0],sparse=c.depth[1],certification_times=times,events=events,full_top20_matches_old=full[:20]==old['full']['orderedPointIdsTop101'][:20],full_top100_matches_old=full[:100]==old['full']['orderedPointIdsTop101'][:100],dense_prefix_mismatches=sum(x!=y for x,y in zip(a[:5000],old['densePrefixPointIds'])),sparse_prefix_mismatches=sum(x!=y for x,y in zip(b[:5000],old['sparsePositivePrefixPointIds'])),independent_checks=checks,seconds=time.time()-start,provenance='Reconstructed complete rankings; sparse accumulation in original term-id order. Not a claim of identity with frozen segment-specific arithmetic.')
 done.write_text(json.dumps(row,indent=2));rows.append(row);print(ds,qid,'COMPLETE',times[20],'old_top20',row['full_top20_matches_old'],'seconds',round(row['seconds'],2),flush=True)
pd.DataFrame([{k:v for k,v in r.items() if k not in ('certification_times','events')} for r in rows]).to_csv(p/'completion-summary.csv',index=False)
