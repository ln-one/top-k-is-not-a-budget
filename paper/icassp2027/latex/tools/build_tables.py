"""Regenerate manuscript tables and audit numbers from frozen repository CSVs."""
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
BUDGETS = (128, 256, 512, 1024, 2048, 4096, 8192, 10000)
SETS = (
    ('msmarco-passage-trec-dl-2019', 'TREC-DL 2019', 43),
    ('msmarco-passage-trec-dl-2020', 'TREC-DL 2020', 54),
    ('nfcorpus', 'NFCorpus', 323),
    ('scifact', 'SciFact', 300),
    ('trec-covid', 'TREC-COVID', 50),
)

def rows(path):
    with (ROOT / path).open(newline='') as f:
        return list(csv.DictReader(f))

curves = defaultdict(list)
for r in rows('results/anytime-five-datasets-chunk64/derived/anytime_frontier_per_query.csv'):
    if r['policy'] in ('balanced', 'pressure', 'blocker'):
        curves[r['dataset'], r['query_id'], r['policy']].append(
            (int(r['work_budget']), int(r['certified_k_cap100'])))
areas = defaultdict(list)
for (dataset, query, policy), points in curves.items():
    points.sort()
    assert tuple(b for b, _ in points) == BUDGETS, (dataset, query, policy)
    area = sum((math.log(b2)-math.log(b1))*(k1+k2)/200
               for (b1,k1),(b2,k2) in zip(points, points[1:]))
    areas[dataset, policy].append(area / math.log(BUDGETS[-1]/BUDGETS[0]))
static = []
for dataset, label, count in SETS:
    assert all(len(areas[dataset,p]) == count for p in ('balanced','pressure','blocker'))
    a,b,c = (mean(areas[dataset,p]) for p in ('balanced','pressure','blocker'))
    static.append(dict(dataset=dataset, balanced=a, pressure=b, dibud=c, relative_gain_pct=100*(c/a-1)))
lines = [r'\begin{table}[t]',r'\centering',
    r'\caption{Normalized certified-prefix area over the read-budget range, capped at 100 results. Higher is better.}',
    r'\label{tab:static}',r'\begin{tabular}{lrrr}',r'\toprule',
    r'Query set & Balanced & Pressure & DiBud \\',r'\midrule']
for (_, label, _), r in zip(SETS,static):
    lines.append(f"{label} & {r['balanced']:.4f} & {r['pressure']:.4f} & {r['dibud']:.4f}" + r' \\')
lines += [r'\bottomrule',r'\end{tabular}',r'\end{table}']
(HERE/'tables/static.tex').write_text('\n'.join(lines)+'\n')
macro = [r for r in rows('results/matched-budget-truncation/macro.csv')
         if r['budget']=='2048' and r['method'] in ('balanced_cert','blocker_cert')]
assert len(macro)==4
source = rows('results/temporal-matched/aggregate.csv')
temporal=[]
lines = [r'\begin{table}[t]',r'\centering',
    r'\caption{Mean certified count for the same 30 queries across five corpus snapshots, with a budget of 2048 reads and a reporting cap of 20.}',
    r'\label{tab:temporal}',r'\begin{tabular}{lrr}',r'\toprule',
    r'Snapshot & Balanced & DiBud \\',r'\midrule']
for i in range(1,6):
    matches=[r for r in source if r['dataset']==f'trec-covid-chrono-r{i}' and r['budget']=='2048' and r['cap']=='20' and r['method'] in ('balanced_cert','blocker_cert')]
    assert len(matches)==2 and all(r['queries']=='30' for r in matches)
    vals={r['method']:float(r['returned']) for r in matches}
    temporal.append(dict(round=i,**vals))
    lines.append(f"Round {i} & {vals['balanced_cert']:.2f} & {vals['blocker_cert']:.2f}" + r' \\')
lines += [r'\bottomrule',r'\end{tabular}',r'\end{table}']
(HERE/'tables/temporal.tex').write_text('\n'.join(lines)+'\n')
audit=dict(static=static, macro_2048=[{k:r[k] for k in ('budget','cap','method','returned')} for r in macro],temporal=temporal)
(HERE/'result-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print(json.dumps(audit,indent=2))
