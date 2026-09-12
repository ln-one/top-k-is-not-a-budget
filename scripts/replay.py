"""Frozen-list experiments: matched schedules, exact prefixes and depth transfer.

No source-generation calls. Grouped maintenance preserves the array certificate.
Saved prefix ends are observation limits, not source exhaustion.
"""
import argparse,csv,hashlib,json,math,time,platform
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from certifier import GroupedFrontier
from rank_bounds import UnequalDepthCertificate,position_score,tie_key,load_qrels
from rank_bounds import DATASETS
BUDGETS=(128,256,512,1024,2048,4096,8192,10000)
LS=(10,20,50,100,200,500,1000,2000,5000)
KS=(5,10,20,50,100)

def dumpcsv(path,rows):
    if not rows:return
    with path.open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def ndcg(ids,jud,k):
    ideal=sum(max(0,v)/math.log2(i+2) for i,v in enumerate(sorted(jud.values(),reverse=True)[:k]))
    return sum(max(0,jud.get(x,0))/math.log2(i+2) for i,x in enumerate(ids[:k]))/ideal if ideal else 0.
def preferred(c,policy,turn,amount):
    available=[i for i in (0,1) if not (c.depth[i]==c.maximum[i] and c.exhausted[i])]
    if not available:return None
    if len(available)==1:return available[0]
    if policy=='balanced':return turn%2
    if c.blocker is not None and c.blocker[3] in (1,2):return 1 if c.blocker[3]==1 else 0
    drops=[]
    for i in (0,1):
        after=c.depth[i]+amount
        end=0. if c.exhausted[i] and after>=c.maximum[i] else float(position_score(after+1))
        drops.append(c.unread(i)-end)
    return 0 if drops[0]>=drops[1] else 1

def one(job):
    ds,snapshot,path,run,jud,verify=job
    data=json.loads(Path(path).read_text());assert data['status']=='ok'
    a=data['densePrefixPointIds'];b=data['sparsePositivePrefixPointIds'];qid=str(data['queryId'])
    assert len(set(a))==len(a) and len(set(b))==len(b)
    full=data['full']['orderedPointIdsTop101'][:100];external=data['full']['orderedExternalIdsTop100']
    mapping=dict(zip(a,data['densePrefixExternalIds'],strict=True));mapping.update(zip(b,data['sparsePositivePrefixExternalIds'],strict=True))
    docs=int(run['documents']);ex=(len(a)==docs,len(b)==docs or len(b)<max(run['parameters']['depths']))
    base=dict(dataset=ds,snapshot=snapshot,query_id=qid)
    budgetrows=[];costrows=[];events=[];transfer=[];audits=0
    full20=ndcg(external,jud,20)
    for batch in (1,64):
      for policy in ('dibud','balanced'):
        c=GroupedFrontier(a,b,ex);c.frontier();turn=0;times={0:0};status='budget';endpoint={};start=time.perf_counter()
        ref=UnequalDepthCertificate(a,b,first_exhausted=ex[0],second_exhausted=ex[1]) if verify else None
        for B in BUDGETS:
          while sum(c.depth)<B and len(c.output)<100:
            ch=preferred(c,policy,turn,min(batch,B-sum(c.depth)))
            if ch is None:status='exhausted';break
            if c.depth[ch]==c.maximum[ch]:status='observation_limit';break
            n=min(batch,B-sum(c.depth),c.maximum[ch]-c.depth[ch]);prior=len(c.output)
            c.read(ch,n);turn+=1;c.frontier();spent=sum(c.depth)
            assert spent<=B and c.output==full[:len(c.output)],(ds,qid,policy,batch,spent)
            if ref is not None:
                r=ref.frontier(*c.depth);assert tuple(c.output)==r.output,(ds,qid,'reference mismatch');audits+=1
            if len(c.output)>prior:
                for k in range(prior+1,len(c.output)+1):times[k]=spent
                events.append(dict(**base,policy=policy,batch=batch,accesses=spent,dense=c.depth[0],sparse=c.depth[1],before=prior,k=len(c.output)))
          if len(c.output)>=100:status='cap100'
          known=status!='observation_limit'
          k=len(c.output);spent=sum(c.depth)
          endpoint[B]=(spent,k,known,status)
          budgetrows.append(dict(**base,policy=policy,batch=batch,budget=B,accesses=spent,dense=c.depth[0],sparse=c.depth[1],known=int(known),stop=status,k=k,k_lower=k,k_upper=k if known else 100,k20=min(k,20),ndcg20=ndcg(external[:min(k,20)],jud,20),full_ndcg20=full20))
          if status=='observation_limit':
            # Keep lower/upper bounds at every later endpoint; no artificial switch.
            pass
        total=sum(c.depth)
        for k in range(1,101):
            costrows.append(dict(**base,policy=policy,batch=batch,k=k,completed=int(k in times),cost=times.get(k,''),lower_bound=times.get(k,total+1 if status!='exhausted' else total),terminal_accesses=total,stop=status))
        # Budget-limited Top20 comparison stops early once 20 are certified.
        for r in budgetrows[-len(BUDGETS):]:
            r['cost20']=times.get(20,'')
            r['baseline20_complete']=int(20 in times)
            r['budget20_cost']=min(r['budget'],times[20]) if 20 in times else (r['budget'] if r['known'] else '')
            r['elapsed_seconds']=time.perf_counter()-start
    # Fixed-L fusion, no imputation experiment: existing zero-fill semantics.
    for L in LS:
        if (len(a)<L and not ex[0]) or (len(b)<L and not ex[1]):continue
        scores={}
        for stream in (a[:L],b[:L]):
            for rank,x in enumerate(stream,1):scores[x]=np.float32(scores.get(x,np.float32(0))+position_score(rank))
        order=sorted(scores,key=lambda x:(-float(scores[x]),tie_key(x)))[:100]
        ext=[mapping[x] for x in order]
        transfer.append(dict(**base,L=L,accesses=min(L,len(a))+min(L,len(b)),ndcg10=ndcg(ext,jud,10),full_ndcg10=ndcg(external,jud,10),ordered20=int(order[:20]==full[:20]),overlap20=len(set(order[:20])&set(full[:20]))/20))
    return budgetrows,costrows,events,transfer,dict(**base,path=path,sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),dense_length=len(a),sparse_length=len(b),dense_exhausted=ex[0],sparse_exhausted=ex[1],array_checks=audits)

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--smoke',action='store_true');p.add_argument('--temporal-only',action='store_true');p.add_argument('--data-root',type=Path,default=Path('data/inputs'));p.add_argument('--workers',type=int,default=4);args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=False);root=args.data_root;jobs=[];sources=[]
    roots=[(ds,0,root/'experiments/target-validity/static-v3'/ds) for ds in DATASETS]
    roots += [(f'trec-covid-chrono-r{i}',i,root/'experiments/target-validity/chronological-v1'/f'round-{i}') for i in range(1,6)]
    if args.temporal_only:roots=[v for v in roots if v[1]>0]
    for ds,snapshot,folder in roots:
        runpath=folder/'run.json';run=json.loads(runpath.read_text());assert run['parameters']['rrfK']==60 and run['parameters']['weights']==[1.,1.]
        qp=root/'datasets'/ds/'source/qrels.tsv';jud=load_qrels(qp)
        for file in (runpath,qp):sources.append(dict(path=str(file),sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
        paths=list((folder/'queries').glob('*.json'));paths.sort(key=lambda path:hashlib.sha256((ds+'/'+str(json.loads(path.read_text())['queryId'])).encode()).hexdigest())
        if args.smoke:paths=paths[:2]
        for path in paths:
            qid=str(json.loads(path.read_text())['queryId']);jobs.append((ds,snapshot,str(path),run,jud.get(qid,{}),args.smoke))
    (args.output/'protocol.json').write_text(json.dumps(dict(budgets=BUDGETS,L=LS,seed=20260910,smoke=args.smoke,jobs=len(jobs),quality_targets=[.9,.95,.99],quality_selection='five-fold held-out, ratio of mean nDCG20; minimum calibration budget meeting target',budget_cost='same SNRA trajectory, early stop at 20, observation limits retained'),indent=2))
    collections=[[],[],[],[],[]];start=time.perf_counter()
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
      for idx,result in enumerate(pool.map(one,jobs),1):
        for coll,part in zip(collections,result):coll.extend(part if isinstance(part,list) else [part])
        if idx%10==0:print(f'Completed {idx}/{len(jobs)}, elapsed {time.perf_counter()-start:.1f}s',flush=True)
    for name,rows in zip(('budget-yield.csv','fixed-k.csv','trajectory-events.csv','transfer-grid.csv'),collections[:4]):dumpcsv(args.output/name,rows)
    (args.output/'input-audit.json').write_text(json.dumps(collections[4],indent=2))
    scripts=['replay.py','certifier.py','rank_bounds.py']
    (args.output/'manifest.json').write_text(json.dumps(dict(real_data=True,jobs=len(jobs),smoke=args.smoke,sources=sources,script_hashes={s:hashlib.sha256((Path('scripts')/s).read_bytes()).hexdigest() for s in scripts},python=platform.python_version(),numpy=np.__version__,seconds=time.perf_counter()-start,array_checks=sum(x['array_checks'] for x in collections[4])),indent=2))
    print('DONE',args.output,time.perf_counter()-start,flush=True)
if __name__=='__main__':main()
