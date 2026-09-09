# Task Packet

- Scope: determine whether exact-certification difficulty and the poison-query
  fraction rise with requested K, then diagnose the responsible rank geometry.
- Files to read:
  - frozen target-validity `run.json` and per-query records for TREC-DL 2019/2020
  - EAHR `canonical_runner/synthetic.py` and `fusion.py`
- Files allowed to edit: this `adaptive-top-k` project only.
- Required skills: paper-orchestration, experiment-results-planning,
  figures-python, verification.
- Evidence/data inputs: real frozen exact rank prefixes; no mock measurements.
- Required artifacts: protocol, traceability table, raw manifest, per-query CSV,
  aggregate CSV, mechanism CSV, analysis JSON/Markdown, PNG/SVG figure.
- Rejection checks:
  - no uncensored depth claim beyond rank 5,000;
  - no latency claim from offline replay;
  - no use of qrels to select K or define poison;
  - certified outputs must equal the frozen exhaustive ordered Top-K;
  - 2019 queries 855410 and 443396 must remain identifiable.
- Validation commands:
  - run the replay script twice and compare output hashes;
  - assert 97 queries × 5 K values and zero certified-output mismatch;
  - run `scripts/verify_pilot.py`, Python syntax checks, and `git diff --check`.
