"""Paired, serial, rotated-order replay timings; excludes actual retrieval."""
import argparse,csv,json,time,hashlib,statistics
from pathlib import Path
from collections import defaultdict
from pilot_simple_schedulers import replay as array_replay
from pilot_grouped_frontier import replay as grouped_replay
from run_anytime_frontier_pilot import UnequalDepthCertificate

def main():
    source=Path('results/simple-schedulers-pilot');out=Path('results/grouped-frontier-event-pilot');m=json.loads((source/'manifest.json').read_text());runs={r['dataset']:json.loads(Path(r['path']).read_text()) for r in m['runs']};chosen=defaultdict(list)
    for r in m['sources']:
        if len(chosen[r['dataset']])<10:chosen[r['dataset']].append(r)
    specs=('array-blocker64','array-unit','grouped-blocker64','grouped-unit','grouped-handoff64');rows=[]
    for ds,sources in chosen.items():
        for src in sources:
            d=json.loads(Path(src['path']).read_text());run=runs[ds];a=d['densePrefixPointIds'];b=d['sparsePositivePrefixPointIds'];docs=int(run['documents']);ex=(len(a)==docs,len(b)==docs or len(b)<max(run['parameters']['depths']));full=d['full']['orderedPointIdsTop101'][:100];c=UnequalDepthCertificate(a,b,first_exhausted=ex[0],second_exhausted=ex[1])
            offset=int(hashlib.sha256((ds+'/'+src['query_id']).encode()).hexdigest(),16)%len(specs)
            for rep in range(3):
                start=(offset+rep)%len(specs)
                for spec in specs[start:]+specs[:start]:
                    if spec.startswith('array-'):rs=array_replay(c,full,spec[6:],m['budgets'])
                    else:rs=grouped_replay(a,b,ex,full,m['budgets'],1 if spec=='grouped-unit' else 64,event=spec=='grouped-handoff64')
                    r=rs[-1];rows.append(dict(dataset=ds,query_id=src['query_id'],repetition=rep,policy=spec,seconds=r['replay_seconds'],calls=r['certificate_calls'],k100=r['k100']))
        print('Benchmarked',ds,flush=True)
    with (out/'timing-paired.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    result=[]
    for spec in specs:
        vals=[float(r['seconds']) for r in rows if r['policy']==spec]
        result.append(dict(policy=spec,mean_ms=statistics.mean(vals)*1000,median_ms=statistics.median(vals)*1000,runs=len(vals)))
    (out/'timing-summary.json').write_text(json.dumps(dict(queries=50,repeats=3,workers=1,order='deterministically rotated',includes='scheduler and certification, excludes initialization and corpus retrieval',results=result),indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
