"""Screen simple evidence-boundary batching rules on frozen exact rank streams."""
import argparse,csv,hashlib,json,math,time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from statistics import mean
import numpy as np
from run_anytime_frontier_pilot import UnequalDepthCertificate, position_score

DATASETS=('msmarco-passage-trec-dl-2019','msmarco-passage-trec-dl-2020','nfcorpus','scifact','trec-covid')
BUDGETS=(128,256,512,1024,2048)
POLICIES=('balanced64','blocker64','pressure64','unit','handoff64','handoff','certificate-event')

def crossing(depth,target,limit):
    # First new depth with a strictly smaller unread contribution, using exactly
    # the replay's float32 rank contribution. No future rank identities accessed.
    if target<=0 or not math.isfinite(target):return 1
    if float(position_score(depth+limit+1))>=target:return limit
    lo,hi=1,limit
    while lo<hi:
        mid=(lo+hi)//2
        if float(position_score(depth+mid+1))<target:hi=mid
        else:lo=mid+1
    return lo

def event_amount(cert,s,depths,ch,limit,kind):
    x=s.next_candidate
    if x is None:return 1
    lower=float(s.lower[x]);seen=s.seen_first|s.seen_second
    eligible=seen.copy();eligible[x]=False
    # Identities in the returned prefix are known observations, not hidden ranks.
    eligible[[cert.observed_index[p] for p in s.output]]=False
    missing=~(s.seen_first if ch==0 else s.seen_second)
    other=1-ch
    maxes=(cert.first_max,cert.second_max)
    exhausted=(cert.first_exhausted,cert.second_exhausted)
    other_u=0.0 if depths[other]==maxes[other] and exhausted[other] else float(position_score(depths[other]+1))
    if kind=='certificate-event':
        base=float(s.lower[s.blocker]) if s.blocker is not None and missing[s.blocker] else other_u
        return crossing(depths[ch],lower-base,limit)
    # On this channel all still-missing observed upper bounds share the same
    # decreasing term u_i. The unseen upper bound also shares this term.
    moving=eligible&missing;fixed=eligible&~missing
    base=max(other_u,float(np.max(s.lower[moving])) if np.any(moving) else -math.inf)
    boundary=max(lower,float(np.max(s.upper[fixed])) if np.any(fixed) else -math.inf)
    return crossing(depths[ch],boundary-base,limit)

def replay(cert,full,policy,budgets):
    depths=[0,0];s=cert.frontier(0,0);calls=1;turn=0;elapsed=0.;decide=0.;out=[]
    maxes=(cert.first_max,cert.second_max)
    for B in budgets:
        start=time.perf_counter()
        while sum(depths)<min(B,sum(maxes)) and s.certified_k<100:
            remaining=B-sum(depths)
            tick=time.perf_counter()
            if policy=='balanced64':
                ch=turn%2;turn+=1
                if depths[ch]>=maxes[ch]:ch=1-ch
                amount=min(64,remaining)
            else:
                quantum=min(1 if policy in ('unit','handoff','certificate-event') else 64,remaining)
                ch=cert.choose_pressure(s,*depths,quantum) if policy=='pressure64' else cert.choose_blocker(s,*depths,quantum)
                amount=quantum
                if policy in ('handoff64','handoff','certificate-event'):
                    limit=min(remaining,maxes[ch]-depths[ch],64 if policy=='handoff64' else remaining)
                    amount=event_amount(cert,s,depths,ch,limit,policy)
            amount=min(amount,remaining,maxes[ch]-depths[ch]);assert amount>0
            decide+=time.perf_counter()-tick
            before=s.output;depths[ch]+=amount;s=cert.frontier(*depths);calls+=1
            assert s.output[:len(before)]==before,'prefix regressed'
            assert sum(depths)<=B
        elapsed+=time.perf_counter()-start
        assert list(s.output)==full[:s.certified_k],(policy,B,'incorrect prefix')
        out.append(dict(policy=policy,budget=B,reads=sum(depths),dense=depths[0],sparse=depths[1],k100=s.certified_k,k20=min(20,s.certified_k),certificate_calls=calls,replay_seconds=elapsed,schedule_seconds=decide))
    return out

def run_query(job):
    ds,path,run,budgets=job
    data=json.loads(Path(path).read_text());assert data['status']=='ok'
    a=data['densePrefixPointIds'];b=data['sparsePositivePrefixPointIds'];docs=int(run['documents'])
    cert=UnequalDepthCertificate(a,b,first_exhausted=len(a)==docs,second_exhausted=len(b)==docs or len(b)<max(run['parameters']['depths']))
    cert.observed_index={str(p):i for i,p in enumerate(cert.identities)}
    # Rotate execution order deterministically to reduce fixed warmup-order bias.
    qid=str(data['queryId']);offset=int(hashlib.sha256((ds+'/'+qid).encode()).hexdigest(),16)%len(POLICIES)
    order=POLICIES[offset:]+POLICIES[:offset];rows=[]
    for policy in order:
        rows += [dict(dataset=ds,query_id=qid,**r) for r in replay(cert,data['full']['orderedPointIdsTop101'][:100],policy,budgets)]
    return rows,dict(dataset=ds,query_id=qid,path=path,sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())

def main():
    p=argparse.ArgumentParser();p.add_argument('--data-root',type=Path,default=Path('data/inputs'));p.add_argument('--output',type=Path,required=True);p.add_argument('--queries',type=int,default=20);p.add_argument('--workers',type=int,default=4);p.add_argument('--max-budget',type=int,default=2048);args=p.parse_args()
    budgets=tuple(b for b in BUDGETS if b<=args.max_budget);jobs=[];runs=[]
    for ds in DATASETS:
        root=args.data_root/'experiments/target-validity/static-v3'/ds;rp=root/'run.json';run=json.loads(rp.read_text());assert run['parameters']['rrfK']==60 and run['parameters']['weights']==[1.0,1.0]
        paths=list((root/'queries').glob('*.json'))
        qids={str(path):str(json.loads(path.read_text())['queryId']) for path in paths}
        paths.sort(key=lambda path:hashlib.sha256((ds+'/'+qids[str(path)]).encode()).hexdigest())
        jobs += [(ds,str(path),run,budgets) for path in paths[:args.queries]]
        runs.append(dict(dataset=ds,path=str(rp),sha256=hashlib.sha256(rp.read_bytes()).hexdigest()))
    args.output.mkdir(parents=True,exist_ok=True);rows=[];sources=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for idx,(new,source) in enumerate(pool.map(run_query,jobs),1):
            rows+=new;sources.append(source)
            if idx%5==0:print(f'Completed {idx}/{len(jobs)} queries',flush=True)
    with (args.output/'per-query.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    manifest=dict(protocol='plan/research/parameter-free-scheduler-pilot.md',queries_per_dataset=args.queries,budgets=budgets,policies=POLICIES,real_data=True,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),sources=sources,runs=runs)
    (args.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    summarize(rows,args.output,budgets)

def summarize(rows,out,budgets):
    groups=defaultdict(list)
    for r in rows:groups[r['dataset'],r['query_id'],r['policy']].append(r)
    scores={}
    for key,rs in groups.items():
        rs.sort(key=lambda r:r['budget'])
        scores[key]=sum(math.log(b['budget']/a['budget'])*(a['k100']+b['k100'])/200 for a,b in zip(rs,rs[1:]))/math.log(budgets[-1]/budgets[0])
    agg=[]
    for ds in DATASETS:
        for policy in POLICIES:
            keys=[k for k in scores if k[0]==ds and k[2]==policy];deltas=[scores[k]-scores[k[0],k[1],'blocker64'] for k in keys];last=[r for r in rows if r['dataset']==ds and r['policy']==policy and r['budget']==budgets[-1]]
            agg.append(dict(dataset=ds,policy=policy,n=len(keys),auc=mean(scores[k] for k in keys),delta_auc=mean(deltas),wins=sum(d>1e-12 for d in deltas),ties=sum(abs(d)<=1e-12 for d in deltas),losses=sum(d< -1e-12 for d in deltas),k100=mean(r['k100'] for r in last),k20=mean(r['k20'] for r in last),certificate_calls=mean(r['certificate_calls'] for r in last),replay_seconds=mean(r['replay_seconds'] for r in last),schedule_seconds=mean(r['schedule_seconds'] for r in last)))
    with (out/'aggregate.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(agg[0]));w.writeheader();w.writerows(agg)
    for policy in POLICIES:
        a=[r for r in agg if r['policy']==policy]
        print(policy,'auc',round(mean(r['auc'] for r in a),6),'delta',round(mean(r['delta_auc'] for r in a),6),'K',round(mean(r['k100'] for r in a),3),'calls',round(mean(r['certificate_calls'] for r in a),1),'time',round(mean(r['replay_seconds'] for r in a),4),flush=True)

if __name__=='__main__':main()
