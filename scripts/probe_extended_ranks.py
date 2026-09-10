import sys,ctypes,json,time,uuid
from pathlib import Path
import numpy as np,pandas as pd,pyarrow.parquet as pq
ROOT=Path(__file__).resolve().parents[1];ART=ROOT.parent/'artifacts/canonical-v1';OUT=ROOT/'results/completion-extension-v1';ds=sys.argv[1] if len(sys.argv)>1 else 'trec-covid'
fixed=pd.read_csv(ROOT/'results/paper-experiments-v2/fixed-k.csv',dtype={'query_id':str})
ids=set(fixed.loc[(fixed.dataset==ds)&(fixed.policy=='dibud')&(fixed.batch==1)&(fixed.k==20)&(fixed.completed==0),'query_id'])
records={}
for p in (ROOT/'data/inputs/experiments/target-validity/static-v3'/ds/'queries').glob('*.json'):
 d=json.loads(p.read_text())
 if str(d['queryId']) in ids:records[str(d['queryId'])]=d
qids=sorted(records);nq=len(qids);base=ART/'datasets'/ds;out=OUT/ds;out.mkdir(exist_ok=True)
lib=ctypes.CDLL(str(OUT/'kernels.dylib'));ptr=lambda a:ctypes.c_void_p(a.ctypes.data)
qp=pq.read_table(base/'dense/bge-small-en-v1.5-f32/queries-000000.parquet').to_pylist();qd={r['id']:r['vector'] for r in qp};q=np.array([qd[i] for i in qids],dtype=np.float32);lib.normalize(ptr(q),nq)
qp=pq.read_table(base/'sparse/bm25-impact-v1/queries-000000.parquet').to_pylist();qd={r['id']:r for r in qp};qi=np.array([v for k in qids for v in qd[k]['indices']],dtype=np.int32);qv=np.array([v for k in qids for v in qd[k]['values']],dtype=np.float32);qo=np.array([0]+list(np.cumsum([len(qd[k]['indices']) for k in qids])),dtype=np.int32)
start=time.time();allids=[];scores=[]
for f in sorted((base/'dense/bge-small-en-v1.5-f32').glob('documents-*.parquet')):
 t=pq.read_table(f);x=t['vector'].combine_chunks().values.to_numpy().reshape(-1,384).copy();lib.normalize(ptr(x),len(x));y=np.empty((len(x),nq),np.float32);lib.dense(ptr(x),len(x),ptr(q),nq,ptr(y));allids.extend(t['id'].to_pylist());scores.append(y)
 print('dense',f.name,len(allids),round(time.time()-start,2),flush=True)
 if len(scores)%20==0:pass
D=np.concatenate(scores);del scores;np.save(out/'dense-scores.npy',D)
lookup={v:i for i,v in enumerate(allids)};S=np.zeros_like(D)
for f in sorted((base/'sparse/bm25-impact-v1').glob('documents-*.parquet')):
 t=pq.read_table(f);idx=t['indices'].combine_chunks();val=t['values'].combine_chunks();o=idx.offsets.to_numpy();ii=idx.values.to_numpy();v=val.values.to_numpy();y=np.empty((len(t),nq),np.float32);lib.sparse(ptr(o),ptr(ii),ptr(v),len(t),ptr(qo),ptr(qi),ptr(qv),nq,ptr(y));S[[lookup[i] for i in t['id'].to_pylist()]]=y
 print('sparse',f.name,round(time.time()-start,2),flush=True)
np.save(out/'sparse-scores.npy',S);(out/'ids.json').write_text(json.dumps(allids));(out/'queries.json').write_text(json.dumps(qids))
ns=uuid.UUID('a0541185-c167-51be-9665-4c5e739d75d3');id_ds='msmarco-passage-trec-dl-2019' if 'msmarco' in ds else ds
cached=OUT/'msmarco-passage-trec-dl-2019/uuids.npy'
if ds=='msmarco-passage-trec-dl-2020' and cached.exists():
 assert json.loads((cached.parent/'ids.json').read_text())==allids
 uu=np.load(cached,mmap_mode='r');(out/'uuids.npy').symlink_to(cached.resolve()) if not (out/'uuids.npy').exists() else None
else:
 uu=np.array([str(uuid.uuid5(ns,f'{id_ds}\x1f{i}')) for i in allids]);np.save(out/'uuids.npy',uu)
report=[]
for j,qid in enumerate(qids):
 d=records[qid]
 for name,score,key in [('dense',D[:,j],'densePrefixPointIds'),('sparse',S[:,j],'sparsePositivePrefixPointIds')]:
  order=np.lexsort((uu,-score));order=order[score[order]>0] if name=='sparse' else order
  old=d[key];actual=uu[order[:len(old)]].tolist();mis=[i for i,(x,y) in enumerate(zip(old,actual)) if x!=y];report.append(dict(query=qid,channel=name,mismatches=len(mis),first=mis[:8]))
  np.save(out/f'{qid}-{name}-order.npy',order)
print(json.dumps(report,indent=2));(out/'prefix-check.json').write_text(json.dumps(report,indent=2));print('seconds',time.time()-start)
