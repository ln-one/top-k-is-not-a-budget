# Task Packet 07: aggregate exact-MIPS index for EAHR

## Scope

Invent, implement, and falsify a physically progressive exact Dense ranked
stream that can replace the eager PVS/scan source at the EAHR fusion boundary.
The index must avoid any query-time per-vector pass before its first exact
output.  Approximate proposals may guide search, but every emitted identity and
its order must be exact over the eligible universe.

## Files to read

- `plan/research/physical-first-output-bound.md`
- `plan/research/fully-incremental-dense-branch.md`
- `plan/research/prior-art-map.md`
- EAHR exact stream and Dense cursor code discovered through CodeGraph
- frozen SciFact and 8.84M MS MARCO physical pilot manifests

## Files allowed to edit

- This `adaptive-top-k` research repository
- A new isolated research module/example in the EAHR `research` repository only
  after the prototype and interface contract are locked

Production-path edits are out of scope until a candidate passes offline gates.

## Required skills

- `using-research-writing`
- `paper-orchestration`
- `literature-review`
- `nature-academic-search`
- `experiment-results-planning`
- `verification` before any completion claim

## Required artifacts

1. `plan/aggregate-index/protocol.md`
2. `plan/aggregate-index/prior-art-and-claims.md`
3. `plan/aggregate-index/candidate-designs.md`
4. deterministic prototype code and raw/derived logs
5. exact-order verifier against exhaustive f32 scoring
6. at least two real-collection evaluations if any candidate survives SciFact
7. physical-work, time-to-first, time-to-rank, memory, build-cost, and collapse
   analysis
8. final go/no-go memo and capability-use audit

## Hard rejection checks

- Any query-time loop that computes a query-dependent bound for every vector
  before first output fails the goal, even if the bound is quantized.
- Any emitted rank disagreement or tie-order disagreement fails exactness.
- ANN recall is not a substitute for a safe unseen-region upper bound.
- A candidate that saves fewer than 20% of physical scoring/bound work on the
  majority of tested real workloads does not satisfy the planning gate.
- Median-only gains are insufficient; p95/p99 and full-scan collapse cases must
  be disclosed.
- Index construction and memory overhead must be reported, not hidden.

## Validation commands

- Unit/exhaustive tests on adversarial low-dimensional collections.
- Random complete-order equality against exhaustive f32 dot products.
- Deterministic replay over frozen query/document manifests.
- Compiler, formatter, test suite, and report hash checks.

