#!/usr/bin/env python3
"""Package only hashed replay inputs; no embeddings or full text corpus."""
import argparse,hashlib,json,tarfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--data-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();sources={}
for mf in ('results/anytime-five-datasets-chunk64/raw/anytime_frontier_manifest.json','results/temporal-prefix/source-manifest.json'):
 for e in json.loads(Path(mf).read_text())['sources']:
  rel=(e['relative_path'] if 'relative_path' in e else e['path'].split('canonical-v1/',1)[1])
  if rel in sources:assert sources[rel]==e['sha256']
  sources[rel]=e['sha256']
a.output.parent.mkdir(parents=True,exist_ok=True)
with tarfile.open(a.output,'w:gz',compresslevel=3) as tar:
 for rel,sha in sorted(sources.items()):
  path=a.data_root/rel;assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
  tar.add(path,arcname=rel,recursive=False)
manifest={'archive':a.output.name,'sha256':hashlib.sha256(a.output.read_bytes()).hexdigest(),'bytes':a.output.stat().st_size,'files':sources}
a.output.with_suffix(a.output.suffix+'.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Packaged',len(sources),'files',manifest['bytes'],'bytes')
