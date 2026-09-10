#!/usr/bin/env python3
"""Reproduce static comparisons, temporal validation, and external metric audits."""
import argparse,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--data-root',type=Path,required=True);p.add_argument('--output',type=Path,default=Path('tmp/reproduction'));a=p.parse_args();root=Path(__file__).resolve().parents[1];data=str(a.data_root.resolve());out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
def run(script,*args):subprocess.run([sys.executable,str(root/'scripts'/script),*map(str,args)],cwd=root,check=True)
run('run_matched_budget_truncation.py','--data-root',data,'--output',out/'static')
run('audit_retrieval_metrics.py','--data-root',data,'--input',out/'static','--output',out/'static-metrics')
run('run_temporal_prefix.py','--data-root',data,'--output',out/'temporal-prefix')
run('run_matched_budget_truncation.py','--data-root',data,'--manifest',out/'temporal-prefix/source-manifest.json','--trace',out/'temporal-prefix/trace.csv','--output',out/'temporal')
run('audit_retrieval_metrics.py','--data-root',data,'--manifest',out/'temporal-prefix/source-manifest.json','--input',out/'temporal','--output',out/'temporal-metrics')
print('Completed:',out)
