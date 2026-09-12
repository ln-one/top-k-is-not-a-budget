"""Uniform full-corpus rank reconstruction and budget/Top20 evaluation.
No old rank prefix is inserted. Float32 sparse sums use original term-id order.
"""
import os
import argparse,ctypes,hashlib,json,time,uuid
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np,pandas as pd,pyarrow.parquet as pq
from certifier import GroupedFrontier
from replay import BUDGETS,LS,preferred,ndcg,dumpcsv
from rank_bounds import position_score,load_qrels,UnequalDepthCertificate
ROOT=Path(__file__).resolve().parents[1]
ART=Path(os.environ.get('DIBUD_ARTIFACTS', ROOT/'data/canonical-v1'))
OUT=Path(os.environ.get('DIBUD_OUTPUT', ROOT/'tmp/static'))
RANKS=Path(os.environ.get('DIBUD_RANKS', ROOT/'data/reconstructed-ranks-v1'))
INPUTS=Path(os.environ.get('DIBUD_INPUTS', ROOT/'data/inputs'))
KERNEL=Path(os.environ.get('DIBUD_KERNEL', ROOT/'data/native/kernels.dylib'))
DS=['nfcorpus','scifact','trec-covid','msmarco-passage-trec-dl-2019','msmarco-passage-trec-dl-2020']+[f'trec-covid-chrono-r{i}' for i in range(1,6)]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(8*1024*1024):h.update(b)
 return h.hexdigest()
def build(ds):
 p=RANKS/ds;p.mkdir(parents=True,exist_ok=True)
 if (p/'complete.json').exists():print('Rank checkpoint',ds,flush=True);return
 start=time.time();base=ART/'datasets'/ds
 old={}
 source=(INPUTS/'experiments/target-validity/chronological-v1'/('round-'+ds.rsplit('r',1)[1])) if 'chrono' in ds else INPUTS/'experiments/target-validity/static-v3'/ds
 for f in (source/'queries').glob('*.json'):
  d=json.loads(f.read_text());old[str(d['queryId'])]=d
 qids=sorted(old);nq=len(qids);(p/'queries.json').write_text(json.dumps(qids))
 dm=json.loads((base/'dense/bge-small-en-v1.5-f32/documents-manifest.json').read_text());sm=json.loads((base/'sparse/bm25-impact-v1/manifest.json').read_text());n=int(sm['source']['documents'])
 lib=ctypes.CDLL(str(KERNEL));ptr=lambda a:ctypes.c_void_p(a.ctypes.data)
 qd={r['id']:r['vector'] for r in pq.read_table(base/'dense/bge-small-en-v1.5-f32/queries-000000.parquet').to_pylist()};q=np.array([qd[i] for i in qids],np.float32);lib.normalize(ptr(q),nq)
 qd={r['id']:r for r in pq.read_table(base/'sparse/bm25-impact-v1/queries-000000.parquet').to_pylist()};qi=np.array([v for k in qids for v in qd[k]['indices']],np.int32);qv=np.array([v for k in qids for v in qd[k]['values']],np.float32);qo=np.array([0]+list(np.cumsum([len(qd[k]['indices']) for k in qids])),np.int32)
 D=np.lib.format.open_memmap(p/'dense-scores.npy',mode='w+',dtype='f4',shape=(n,nq));allids=[];audits=[]
 for i,spec in enumerate(dm['shards']):
  f=base/'dense/bge-small-en-v1.5-f32'/spec['name'];digest=sha(f);assert digest==spec['sha256'];audits.append(dict(path=str(f),sha256=digest))
  t=pq.read_table(f);x=t['vector'].combine_chunks().values.to_numpy().reshape(-1,384).copy();lib.normalize(ptr(x),len(x));offset=len(allids);lib.dense(ptr(x),len(x),ptr(q),nq,ptr(D[offset:offset+len(x)]));allids.extend(t['id'].to_pylist())
  if i%25==0:print(ds,'Dense',len(allids),'/',n,round(time.time()-start,1),'s',flush=True)
 assert len(allids)==n;D.flush();lookup={v:i for i,v in enumerate(allids)};S=np.lib.format.open_memmap(p/'sparse-scores.npy',mode='w+',dtype='f4',shape=(n,nq));S[:]=0
 hashes={f['path']:f['sha256'] for f in sm['files']}
 for i,name in enumerate(sm['shards']['documents']):
  f=base/'sparse/bm25-impact-v1'/name;digest=sha(f);assert digest==hashes[name];audits.append(dict(path=str(f),sha256=digest))
  t=pq.read_table(f);ii=t['indices'].combine_chunks();v=t['values'].combine_chunks();o=ii.offsets.to_numpy();iv=ii.values.to_numpy();vv=v.values.to_numpy();y=np.empty((len(t),nq),np.float32);lib.sparse(ptr(o),ptr(iv),ptr(vv),len(t),ptr(qo),ptr(qi),ptr(qv),nq,ptr(y));S[[lookup[v] for v in t['id'].to_pylist()]]=y
  if i%20==0:print(ds,'Sparse shard',i,round(time.time()-start,1),'s',flush=True)
 S.flush();del lookup
 # Validate query shards and source representation manifests as well.
 for profile,name in [('dense/bge-small-en-v1.5-f32','queries-manifest.json'),('sparse/bm25-impact-v1','manifest.json')]:
  mp=base/profile/name;m=json.loads(mp.read_text());specs=m['shards'] if name=='queries-manifest.json' else [s for s in m['files'] if s['path'] in m['shards']['queries']]
  for spec in specs:
   f=mp.parent/spec.get('name',spec.get('path'));h=sha(f);assert h==spec['sha256'];audits.append(dict(path=str(f),sha256=h))
 (p/'ids.json').write_text(json.dumps(allids));id_ds='msmarco-passage-trec-dl-2019' if 'msmarco' in ds else ds
 cached=ROOT/'results/completion-extension-v1'/id_ds
 if (cached/'uuids.npy').exists():
  assert json.loads((cached/'ids.json').read_text())==allids
  uu=np.load(cached/'uuids.npy',mmap_mode='r')
 else:
  ns=uuid.UUID('a0541185-c167-51be-9665-4c5e739d75d3');uu=np.array([str(uuid.uuid5(ns,f'{id_ds}\x1f{i}')) for i in allids])
 np.save(p/'uuids.npy',uu)
 tieorder=np.argsort(uu);tie=np.empty(n,np.uint32);tie[tieorder]=np.arange(n,dtype=np.uint32);del tieorder
 def order(score,positive=False):
  # Float total-order key followed by UUID rank; every packed key is unique.
  bits=np.ascontiguousarray(score).view(np.uint32);asc=np.where((bits>>31)!=0,~bits,bits^np.uint32(0x80000000));key=((~asc).astype(np.uint64)<<np.uint64(32))|tie
  result=np.argsort(key).astype(np.uint32)
  return result[score[result]>0] if positive else result
 reports=[]
 for j,qid in enumerate(qids):
  dense=order(D[:,j]);sparse=order(S[:,j],True)
  if j==0:
   for score,o in [(D[:,j],dense),(S[:,j],sparse)]:
    # Independent sort of the score band covering the first 6000 positions.
    band=np.flatnonzero(score>=score[o[min(5999,len(o)-1)]]) if len(o) else np.array([],int)
    ref=band[np.lexsort((uu[band],-score[band]))];ref=ref[score[ref]>0] if len(o)<n else ref
    assert np.array_equal(o[:min(5000,len(o))],ref[:min(5000,len(o))])
  np.save(p/f'{qid}-dense.npy',dense);np.save(p/f'{qid}-sparse.npy',sparse)
  (p/f'{qid}-observed.json').write_text(json.dumps({str(uu[i]):allids[i] for i in set(dense[:5000].tolist()+sparse[:5000].tolist())}))
  fused=np.zeros(n,np.float32);fused[dense]=position_score(np.arange(1,n+1));fused[sparse]+=position_score(np.arange(1,len(sparse)+1));ix=np.argpartition(fused,-101)[-101:];ix=np.flatnonzero(fused>=fused[ix].min());ix=ix[np.lexsort((uu[ix],-fused[ix]))][:101]
  full=uu[ix].tolist();meta=dict(dataset=ds,query_id=qid,documents=n,dense_length=n,sparse_length=len(sparse),full=full,external=[allids[i] for i in ix],dense_prefix_mismatches=sum(a!=b for a,b in zip(uu[dense[:len(old[qid]['densePrefixPointIds'])]],old[qid]['densePrefixPointIds'])),sparse_prefix_mismatches=sum(a!=b for a,b in zip(uu[sparse[:len(old[qid]['sparsePositivePrefixPointIds'])]],old[qid]['sparsePositivePrefixPointIds'])),old_top20_equal=full[:20]==old[qid]['full']['orderedPointIdsTop101'][:20],old_top100_equal=full[:100]==old[qid]['full']['orderedPointIdsTop101'][:100],dense_rank_sha256=sha(p/f'{qid}-dense.npy'),sparse_rank_sha256=sha(p/f'{qid}-sparse.npy'))
  (p/f'{qid}.json').write_text(json.dumps(meta));reports.append(meta)
  if j%10==0:print(ds,'ranked',j+1,'/',nq,round(time.time()-start,1),'s',flush=True)
 dumpcsv(p/'comparison-to-v2.csv',[{k:v for k,v in m.items() if k not in ('full','external')} for m in reports]);(p/'complete.json').write_text(json.dumps(dict(dataset=ds,queries=nq,seconds=time.time()-start,sources=audits,protocol='Full Dense NEON float32 cosine; Sparse float32 original-term-id accumulation; ascending stable UUID ties; positive sparse support'),indent=2));print(ds,'RANKS DONE',round(time.time()-start,1),flush=True)
class Stream:
 def __init__(self,uu,order):self.uu=uu;self.order=order
 def __len__(self):return len(self.order)
 def __getitem__(self,i):return self.uu[self.order[i]].tolist() if isinstance(i,slice) else str(self.uu[self.order[i]])
def replay(job):
 ds,qid=job;p=RANKS/ds;dest=OUT/'queries'/ds/f'{qid}.json';dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():return ds,qid,'checkpoint'
 start=time.time();m=json.loads((p/f'{qid}.json').read_text());uu=np.load(p/'uuids.npy',mmap_mode='r');a=Stream(uu,np.load(p/f'{qid}-dense.npy',mmap_mode='r'));b=Stream(uu,np.load(p/f'{qid}-sparse.npy',mmap_mode='r'));full=m['full'];external=m['external'];jud=load_qrels(INPUTS/'datasets'/ds/'source/qrels.tsv').get(qid,{})
 base=dict(dataset=ds,snapshot=int(ds.rsplit('r',1)[1]) if 'chrono' in ds else 0,query_id=qid);bud=[];cost=[];events=[];checks=0
 for batch in (1,64):
  for policy in ('dibud','balanced'):
   c=GroupedFrontier(a,b,(True,True));c.frontier();turn=0;times={};states={}
   def step(amount):
    nonlocal turn
    ch=preferred(c,policy,turn,amount)
    if ch is None:raise RuntimeError('Full corpus exhausted before completion')
    amount=min(amount,c.maximum[ch]-c.depth[ch]);assert amount>0
    prior=len(c.output);c.read(ch,amount);turn+=1;c.frontier();spent=sum(c.depth)
    if len(c.output)>prior:
     assert c.output==full[:len(c.output)]
     for k in range(prior+1,len(c.output)+1):times[k]=spent
     events.append(dict(**base,policy=policy,batch=batch,accesses=spent,dense=c.depth[0],sparse=c.depth[1],before=prior,k=len(c.output)))
     states[tuple(c.depth)]=len(c.output)
   for B in BUDGETS:
    while sum(c.depth)<B and len(c.output)<100:step(min(batch,B-sum(c.depth)))
    spent=sum(c.depth);k=len(c.output);assert spent<=B;states[tuple(c.depth)]=k
    bud.append(dict(**base,policy=policy,batch=batch,budget=B,accesses=spent,dense=c.depth[0],sparse=c.depth[1],known=1,stop='cap100' if k>=100 else 'budget',k=k,k_lower=k,k_upper=k,k20=min(k,20),ndcg20=ndcg(external[:min(k,20)],jud,20),full_ndcg20=ndcg(external,jud,20)))
   # No access cap on the fixed-20 baseline; same schedule continues.
   while len(c.output)<20:step(batch)
   total=sum(c.depth);assert 20 in times
   for k in range(1,101):cost.append(dict(**base,policy=policy,batch=batch,k=k,completed=int(k in times),cost=times.get(k,''),lower_bound=times.get(k,total+1),terminal_accesses=total,stop='complete20' if len(c.output)<100 else 'cap100'))
   for r in bud[-len(BUDGETS):]:r.update(cost20=times[20],baseline20_complete=1,budget20_cost=min(r['budget'],times[20]),elapsed_seconds=time.time()-start)
   # Independent array certifier sees the same observed portions and only
   # receives exhaustion when those portions equal the full channel support.
   ref=UnequalDepthCertificate(a[:c.depth[0]],b[:c.depth[1]],first_exhausted=c.depth[0]==len(a),second_exhausted=c.depth[1]==len(b))
   for (d,s),k in states.items():
    z=ref.frontier(d,s);assert z.output==tuple(full[:k]),(ds,qid,policy,batch,d,s,k);checks+=1
 # Fixed-L scores are obtained from the new rank protocol too.
 # Map only relevant/observed IDs through the preserved external IDs once.
 mp=json.loads((p/f'{qid}-observed.json').read_text())
 transfer=[]
 for L in LS:
  scores={}
  for stream in (a[:L],b[:L]):
   for rank,x in enumerate(stream,1):scores[x]=np.float32(scores.get(x,np.float32(0))+position_score(rank))
  order=sorted(scores,key=lambda x:(-float(scores[x]),x))[:100];ext=[mp[x] for x in order]
  transfer.append(dict(**base,L=L,accesses=min(L,len(a))+min(L,len(b)),ndcg10=ndcg(ext,jud,10),full_ndcg10=ndcg(external,jud,10),ordered20=int(order[:20]==full[:20]),overlap20=len(set(order[:20])&set(full[:20]))/20))
 result=dict(budget=bud,cost=cost,events=events,transfer=transfer,audit=dict(**base,rank_metadata=str(p/f'{qid}.json'),dense_length=len(a),sparse_length=len(b),array_checks=checks,seconds=time.time()-start,all_four_top20_complete=True))
 dest.write_text(json.dumps(result));return ds,qid,round(time.time()-start,2)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--dataset',choices=DS);ap.add_argument('--workers',type=int,default=2);ap.add_argument('--build-only',action='store_true');ap.add_argument('--static-only',action='store_true');args=ap.parse_args();OUT.mkdir(parents=True,exist_ok=True);RANKS.mkdir(parents=True,exist_ok=True)
 selected=[args.dataset] if args.dataset else DS[:5] if args.static_only else DS
 for ds in selected:build(ds)
 if args.build_only:return
 jobs=[(ds,q) for ds in selected for q in json.loads((RANKS/ds/'queries.json').read_text())]
 with ProcessPoolExecutor(max_workers=args.workers) as pool:
  for i,r in enumerate(pool.map(replay,jobs),1):
   if i%10==0 or i==len(jobs):print('REPLAY',i,'/',len(jobs),r,flush=True)
 collections=[[],[],[],[],[]]
 for ds in DS:
  for f in sorted((OUT/'queries'/ds).glob('*.json')):
   x=json.loads(f.read_text())
   for coll,key in zip(collections,['budget','cost','events','transfer','audit']):coll.extend(x[key] if isinstance(x[key],list) else [x[key]])
 for name,rows in zip(['budget-yield.csv','fixed-k.csv','trajectory-events.csv','transfer-grid.csv'],collections):dumpcsv(OUT/name,rows)
 (OUT/'input-audit.json').write_text(json.dumps(collections[-1],indent=2));(OUT/'manifest.json').write_text(json.dumps(dict(queries=len(collections[-1]),all_top20_complete=all(x['all_four_top20_complete'] for x in collections[-1]),array_checks=sum(x['array_checks'] for x in collections[-1]),rank_protocol='reconstructed-ranks-v1',script_sha256=sha(Path(__file__)),budgets=BUDGETS),indent=2))
 print('DONE',len(collections[-1]),flush=True)
if __name__=='__main__':main()
