"""Three-support-group implementation of the same exact-prefix certificate.

Execution optimization, not a new certificate or a claimed novel aggregation
algorithm. No unseen identities are exposed to the scheduler.
"""
import argparse,csv,hashlib,heapq,json,time
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from run_anytime_frontier_pilot import position_score,tie_key

class GroupedFrontier:
    def __init__(self,a,b,exhausted):
        self.streams=(a,b);self.maximum=(len(a),len(b));self.exhausted=exhausted
        self.depth=[0,0];self.docs={};self.heaps={1:[],2:[],3:[]};self.output=[];self.emitted=set();self.calls=0
        self.rank_scores=position_score(np.arange(max(self.maximum)+2,dtype=np.int32))
        self.candidate=None;self.blocker=None
    def unread(self,i,depth=None):
        d=self.depth[i] if depth is None else depth
        return 0. if d==self.maximum[i] and self.exhausted[i] else float(self.rank_scores[d+1])
    def read(self,ch,n):
        end=self.depth[ch]+n
        for rank in range(self.depth[ch]+1,end+1):
            identity=self.streams[ch][rank-1]
            if identity in self.emitted:continue
            mask,score,tie=self.docs.get(identity,(0,0.,tie_key(identity)))
            assert not (mask & (1<<ch))
            mask|=1<<ch;score=float(np.float32(score+self.rank_scores[rank]))
            self.docs[identity]=(mask,score,tie)
            heapq.heappush(self.heaps[mask],(-score,tie,identity))
        self.depth[ch]=end
    def head(self,mask,offset=0.,exclude=None):
        heap=self.heaps[mask];saved=[];best=None
        while heap:
            neg,tie,p=heap[0]
            if p in self.emitted or self.docs[p][0]!=mask:
                heapq.heappop(heap);continue
            score=float(np.float32(-neg+offset))
            if best is not None and score<best[0]:break
            item=heapq.heappop(heap);saved.append(item)
            if p==exclude:continue
            value=(score,tie,p,mask)
            if best is None or (-score,tie)<(-best[0],best[1]):best=value
        for item in saved:heapq.heappush(heap,item)
        return best
    def frontier(self):
        self.calls+=1;u=[self.unread(i) for i in (0,1)];anon=float(np.float32(sum(u)))
        while len(self.output)<100:
            candidates=[v for m in (1,2,3) if (v:=self.head(m)) is not None]
            if not candidates:self.candidate=None;self.blocker=None;break
            x=min(candidates,key=lambda v:(-v[0],v[1]))
            competitors=[v for m in (1,2,3) if (v:=self.head(m,u[1] if m==1 else u[0] if m==2 else 0.,exclude=x[2])) is not None]
            y=min(competitors,key=lambda v:(-v[0],v[1])) if competitors else None
            if x[0]<=anon or (y is not None and (-x[0],x[1])>(-y[0],y[1])):
                self.candidate=x;self.blocker=y if y is not None and y[0]>=anon else None;break
            self.output.append(x[2]);self.emitted.add(x[2])
        return tuple(self.output)
    def choose(self,amount):
        if self.depth[0]>=self.maximum[0]:return 1
        if self.depth[1]>=self.maximum[1]:return 0
        if self.blocker is not None:
            mask=self.blocker[3]
            if mask in (1,2):return 1 if mask==1 else 0
        drop=[self.unread(i)-self.unread(i,min(self.maximum[i],self.depth[i]+amount)) for i in (0,1)]
        return 0 if drop[0]>=drop[1] else 1

def replay(a,b,exhausted,full,budgets,chunk):
    c=GroupedFrontier(a,b,exhausted);c.frontier();rows=[];elapsed=0.
    for B in budgets:
        t=time.perf_counter()
        while sum(c.depth)<min(B,sum(c.maximum)) and len(c.output)<100:
            amount=min(chunk,B-sum(c.depth));ch=c.choose(amount);amount=min(amount,c.maximum[ch]-c.depth[ch]);c.read(ch,amount);c.frontier()
        elapsed+=time.perf_counter()-t
        assert c.output==full[:len(c.output)],'incorrect grouped certificate'
        rows.append(dict(budget=B,reads=sum(c.depth),dense=c.depth[0],sparse=c.depth[1],k100=len(c.output),certificate_calls=c.calls,replay_seconds=elapsed))
    return rows

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=Path('results/simple-schedulers-pilot'));p.add_argument('--output',type=Path,default=Path('results/grouped-frontier-pilot'));args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    m=json.loads((args.source/'manifest.json').read_text());runs={x['dataset']:json.loads(Path(x['path']).read_text()) for x in m['runs']}
    with (args.source/'per-query.csv').open() as f:ref={(r['dataset'],r['query_id'],r['policy'],int(r['budget'])):r for r in csv.DictReader(f)}
    rows=[]
    for idx,src in enumerate(m['sources'],1):
        ds=src['dataset'];qid=src['query_id'];path=Path(src['path']);assert hashlib.sha256(path.read_bytes()).hexdigest()==src['sha256'];d=json.loads(path.read_text());run=runs[ds];a=d['densePrefixPointIds'];b=d['sparsePositivePrefixPointIds'];docs=int(run['documents']);exhausted=(len(a)==docs,len(b)==docs or len(b)<max(run['parameters']['depths']))
        for chunk,policy in ((1,'unit'),(64,'blocker64')):
            for r in replay(a,b,exhausted,d['full']['orderedPointIdsTop101'][:100],m['budgets'],chunk):
                old=ref[ds,qid,policy,r['budget']]
                for k in ('reads','dense','sparse','k100','certificate_calls'):assert int(old[k])==r[k],(ds,qid,policy,k,old[k],r[k])
                rows.append(dict(dataset=ds,query_id=qid,policy='grouped-'+policy,**r))
        if idx%20==0:print(f'Grouped exact match {idx}/{len(m["sources"])}',flush=True)
    with (args.output/'per-query.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (args.output/'manifest.json').write_text(json.dumps(dict(source_manifest=str(args.source/'manifest.json'),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),all_reference_states_equal=True,query_count=len(m['sources']),note='Same certificate and same choices, compressed state maintenance. Times are descriptive single-run Python timings, not end-to-end retrieval latency.'),indent=2)+'\n')

if __name__=='__main__':main()
