"""Verify raw reconstruction inputs against frozen manifests."""
import json,hashlib,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];A=ROOT.parent/'artifacts/canonical-v1';O=ROOT/'results/completion-extension-v1'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(8*1024*1024):h.update(b)
 return h.hexdigest()
seen={};rows=[];start=time.time()
for ds in ['trec-covid','msmarco-passage-trec-dl-2019','msmarco-passage-trec-dl-2020']:
 base=A/'datasets'/ds
 for profile,manifest in [('dense/bge-small-en-v1.5-f32','documents-manifest.json'),('dense/bge-small-en-v1.5-f32','queries-manifest.json'),('sparse/bm25-impact-v1','manifest.json')]:
  p=base/profile/manifest;m=json.loads(p.read_text());specs=m['files'] if 'files' in m else m['shards']
  for sp in specs:
   file=p.parent/sp.get('name',sp.get('path'));st=file.stat();key=(st.st_dev,st.st_ino,st.st_size)
   value=seen.get(key)
   if value is None:value=sha(file);seen[key]=value
   assert value==sp['sha256'],str(file)
   rows.append(dict(path=str(file),sha256=value,bytes=st.st_size))
 print(ds,'verified',len(rows),'files',round(time.time()-start,1),flush=True)
(O/'source-audit.json').write_text(json.dumps(dict(files=rows,all_checksums_match=True,seconds=time.time()-start,scripts={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'scripts/exact_rank_kernels.c',ROOT/'scripts/probe_extended_ranks.py',ROOT/'scripts/replay_extended_completion.py',ROOT/'scripts/replay_dense_only_extension.py']}),indent=2))
