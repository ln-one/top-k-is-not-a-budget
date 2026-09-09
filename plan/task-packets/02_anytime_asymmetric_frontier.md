# Task Packet: Anytime Asymmetric Certified Frontier

- Scope: replace requested Top-K with a continuously growing certified prefix,
  and allocate one total access budget asymmetrically across Dense and Sparse.
- User constraints:
  - no semantic checkpoints such as Top-5, Top-10, or Top-20;
  - K is an output, not an input;
  - Dense and Sparse depths may differ arbitrarily;
  - prefer a simple exact method over a learned or threshold-heavy controller;
  - evaluate several alternatives on real frozen rankings before recommending one.
- Files to read:
  - `scripts/run_topk_pilot.py` and the first pilot outputs;
  - frozen EAHR target-validity prefixes and qrels;
  - primary literature on threshold aggregation, any-k/anytime ranking, and
    resource-bounded query execution.
- Files allowed to edit: this `adaptive-top-k` project only.
- Required artifacts:
  - literature evidence map;
  - generalized unequal-depth certificate implementation;
  - at least three allocation policies plus an offline grid-oracle envelope;
  - per-query and aggregate quality--work results;
  - deterministic verification and two review passes.
- Rejection checks:
  - no qrels or exhaustive ranking may be used by a deployable scheduler;
  - evaluation budget points are not method-side K checkpoints;
  - exactness claims apply only to the prefix actually certified;
  - no claim that a finite parameter-free stopping time exists without an
    external work/latency preference;
  - Dense and Sparse depths must not be forced equal by the interface.
- Validation:
  - every returned prefix equals the corresponding prefix of frozen exhaustive
    WRRF order;
  - the certified prefix length is monotone along every execution trace;
  - total work equals Dense depth plus Sparse depth;
  - replay is deterministic and source hashes are recorded.
