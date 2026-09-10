"""Reuse the locked v2 analysis on a separately versioned, complete-rank run."""
from pathlib import Path
import analyze_paper_experiments_v2 as analysis
if __name__=='__main__':
 analysis.OUT=Path('results/paper-experiments-v3')
 analysis.main(include_temporal=False)
