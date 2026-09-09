# Review pass 1 — methods and data integrity

Date: 2026-08-17

## Checks

- Confirmed the source contract from both frozen `run.json` files: equal
  weights, WRRF rank constant 60, depth 5,000, and certificate limit at least
  101.
- Confirmed 43 TREC-DL 2019 and 54 TREC-DL 2020 records and five K values,
  producing 485 query-K rows.
- Confirmed that qrels are used only for descriptive utility fields, never for
  certificate search, poison classification, or K selection.
- Confirmed every successful certificate output against the frozen exhaustive
  ordered Top-K; the runner aborts on a mismatch.
- Confirmed right-censored cases are represented as depth greater than 5,000,
  not as full-corpus exhaustion.
- Recomputed source and output hashes from the manifest.
- Compared batch sizes 1, 16, and 64. Censor flags, depth-threshold flags,
  ambiguity types, utility fields, and first-censored-K transitions are
  invariant.

## Finding and resolution

The first implementation populated fields named `*_at_5000` from the minimum
certificate depth for successful queries, while failed queries used depth
5,000. This did not affect censoring rates, but it mixed mechanism-analysis
depths. The replay now performs a separate terminal check for every query-K,
uses only that check in all `*_at_5000` fields, and independently verifies both
minimum-depth and terminal outputs against the oracle. All results were rerun.

## Outcome

Pass. No unresolved method/data-integrity issue remains within the stated
offline pilot boundary.
