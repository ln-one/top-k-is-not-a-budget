"""Extend only exactly reconstructed Dense ranks; keep original Sparse prefix."""
import sys,json,time
from pathlib import Path
import numpy as np
from pilot_grouped_frontier import GroupedFrontier
from run_paper_experiments_v2 import preferred
from run_anytime_frontier_pilot import UnequalDepthCertificate
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'results/completion-extension-v1';ds=sys.argv[1];p=out/ds
uu=np.load(p/'uuids.npy',mmap_mode='r');qids=json.loads((p/'queries.json').read_text());records={}
for f in (ROOT/'data/inputs/experiments/target-validity/static-v3'/ds/'queries').glob('*.json'):
 d=json.loads(f.read_text());records[str(d['queryId'])]=d
class Stream:
 def __init__(self,o):self.o=o
 def __len__(self):return len(self.o)
 def __getitem__(self,i):return uu[self.o[i]].tolist() if isinstance(i,slice) else str(uu[self.o[i]])
rows=[]
for qid in qids:
 d=records[qid];a=Stream(np.load(p/f'{qid}-dense-order.npy',mmap_mode='r'));b=d['sparsePositivePrefixPointIds'];assert a[:5000]==d['densePrefixPointIds']
 c=GroupedFrontier(a,b,(True,False));c.frontier();events=[]
 while len(c.output)<20:
  ch=preferred(c,'dibud',0,1)
  if c.depth[ch]==c.maximum[ch]:break
  n=len(c.output);c.read(ch,1);c.frontier()
  assert c.output==d['full']['orderedPointIdsTop101'][:len(c.output)]
  if len(c.output)>n:events.append(dict(dense=c.depth[0],sparse=c.depth[1],k=len(c.output)))
 ref=UnequalDepthCertificate(a[:c.depth[0]],b,first_exhausted=c.depth[0]==len(a),second_exhausted=False)
 for e in events:assert ref.frontier(e['dense'],e['sparse']).output==tuple(d['full']['orderedPointIdsTop101'][:e['k']])
 rows.append(dict(dataset=ds,query_id=qid,completed=len(c.output)>=20,accesses=sum(c.depth),dense=c.depth[0],sparse=c.depth[1],k=len(c.output),independent_checks=len(events),source='Only Dense extended; original Sparse prefix retained without reinterpretation.'))
print(json.dumps(rows,indent=2));(p/'dense-only-extension.json').write_text(json.dumps(rows,indent=2))
