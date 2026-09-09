# Task Packet: replay and strong-baseline expansion

- Scope: Design the next offline study needed to support a CCF-B-or-better
  paper and identify analyses that can already be run on frozen rankings.
- Files to read: `plan/experiment-protocol.md`,
  `plan/review/method-experiment-traceability.md`, all current anytime scripts,
  `results/anytime-frontier-analysis.md`.
- Files allowed to edit: `plan/research/replay-expansion.md` only.
- Required skills: experiment-results-planning.
- Evidence/data inputs: verified pilot CSVs and code; classical algorithms from
  the prior-art task may be referenced provisionally by name.
- Required artifacts: strongest fair baselines; oracle definitions; cost-ratio
  grid; metrics; datasets/backends; poison/tail analysis; statistical plan;
  live-validation bridge; explicit go/no-go thresholds.
- Rejection checks: balanced is not sufficient as the strongest baseline;
  logical depth must not be described as latency; qrels must not leak into the
  online scheduler; oracle must be labeled non-deployable.
- Validation: every proposed claim maps to a runnable experiment and artifact.

