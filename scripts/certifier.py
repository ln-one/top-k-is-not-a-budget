"""Incremental exact-prefix certification with grouped score bounds."""
import heapq
import numpy as np
from rank_bounds import position_score, tie_key
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
