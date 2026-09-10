# Complete-ranking experiment protocol

The user authorized a uniform rebuild after the extension pilot found that the original index snapshots were unavailable. Preserve v2; do not splice reconstructed tails onto old prefixes.

- Reconstruct all five static query sets (770 queries) from the verified canonical Dense and Sparse vector artifacts.
- Dense: original ARM64 float32 NEON cosine preprocessing/dot arithmetic, verified bitwise against frozen Rust source. Sparse: float32 accumulation in ascending original term-ID order, independent of index segmentation. Positive Sparse support only; equal raw scores use ascending stable UUID identities.
- Full-list equal-weight float32 RRF uses 1/(59+r). Compute its full Top-101 independently from complete channel ranks. Compare against old references for diagnostics, but evaluate against each reconstructed reference.
- DiBud and Balanced share the existing certifier, budgets 128 through 10,000, and unit/batch-64 granularity. Record all budget endpoints and certify output up to 100.
- Continue every policy/granularity trajectory until at least 20 results are certified, without the former 10,000-access cap. Only actual channel exhaustion sets its unread bound to zero. Top-20 completion is required on every query; Top-50/100 completion beyond the evaluation budgets is not required and must not be claimed.
- Independently validate all recorded emission states and budget endpoints with the array certifier, and all reported nDCG values with pytrec_eval. Require zero incorrect prefixes, zero budget violations, and 770/770 static Top-20 completions for every policy/granularity pair.
- Retain the existing five-fold partitions, calibration choices, quality targets, metric definitions and bootstrap seed. Recompute every comparison from v3 rankings; do not select queries by favorable results.

This is a full-corpus ranking replay study. Report logical access counts, not end-to-end latency. Large arrays remain local and regenerable; immutable v2 evidence remains available.

## Scope correction after artifact inspection

All five static query sets have complete vector artifacts and are included (770 queries, 3,080 policy/granularity trajectories). The temporal snapshots are excluded from v3: their original Dense document shards are missing, and some source document exports are also missing. Temporal v2 results remain preserved, not merged into v3. No regenerated or substituted temporal corpus is silently introduced.
