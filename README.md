# DiBud

Reproduction code for **Top-K Is Not a Budget for Hybrid Retrieval**.
DiBud takes a ranking-access budget and returns a certified prefix of the full RRF ranking.

## Verify the paper results

```sh
python3 scripts/check_results.py
```

This checks the included records and paper tables without downloading data or models.

## Reproduce

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Follow [the reproduction guide](REPRODUCE.md) to rebuild summaries, replay rankings,
or reconstruct the static rankings from source artifacts.

- [Static results](results/paper-experiments-v3/README.md): 770 queries, five query sets.
- [Depth-transfer results](results/paper-experiments-v2/README.md): query and corpus variation.
- [Paper and build instructions](paper/icassp2027/latex/README.md).

Experiments count ranking accesses. Raw datasets and model artifacts are external inputs.
