"""Exhaustively compare grouped and array certificates on small permutations."""
import itertools,json
from pathlib import Path
from pilot_grouped_frontier import GroupedFrontier
from run_anytime_frontier_pilot import UnequalDepthCertificate

def main():
    a=[f'{i+1:032x}' for i in range(6)];count=0
    for b0 in itertools.permutations(a):
        b=list(b0)
        for flags in ((True,True),(False,False)):
            c=UnequalDepthCertificate(a,b,first_exhausted=flags[0],second_exhausted=flags[1])
            for d in range(7):
                for s in range(7):
                    g=GroupedFrontier(a,b,flags);g.read(0,d);g.read(1,s)
                    assert g.frontier()==c.frontier(d,s).output,(b,d,s,flags)
                    count+=1
    report=dict(n=6,second_permutations=720,exhaustion_cases=2,depth_pairs=49,states_checked=count,mismatches=0)
    Path('results/grouped-frontier-event-pilot/exhaustive-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report)
if __name__=='__main__':main()
