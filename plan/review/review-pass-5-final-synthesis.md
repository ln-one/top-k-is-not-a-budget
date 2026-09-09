# Review pass 5: final synthesis and go/no-go

## Scope

Final audit of `plan/research/final-synthesis-zh.md` against generated replay
reports, the frozen production-scale physical pilot, the prior-art map, and the
paper-path decision.  This pass checks consistency and claim strength; it does
not manufacture a positive paper conclusion.

## Checks

| Check | Evidence | Result |
|---|---|---|
| Ordered poison curve | `results/poison-generalization-five-datasets.md` | 0.00/2.13/13.48/36.28/51.31% reproduced |
| Set-only poison curve | `results/set-certificate-five-datasets.md` | 0.00/0.40/4.61/23.37/34.94% reproduced |
| Quality--budget examples | `results/quality-budget-frontier-five-datasets.md` | Work-128 and work-2048 values reproduced |
| Scheduler correctness | `scripts/verify_anytime_frontier.py` | 3,104 rows; 2,020 random unequal-depth checks; no blocker/grid regret in the audited states |
| Pilot certificate correctness | `scripts/verify_pilot.py` | 97 queries; zero complete-list oracle mismatches |
| Physical audit determinism | `scripts/analyze_e5_scale_physical.py` | Rebuilt report byte-identically; SHA-256 `9f81279612f0173763617feb77d5590cee6a1addb2701f030f8511fdea98406c` |
| Physical/logical boundary | CodeGraph audit plus frozen 8.84M-document pilot | All-row int8 preparation disclosed; no latency claim inferred from logical depth |
| Novelty boundary | `plan/research/prior-art-map.md` and `plan/research/wrrf-lara-reduction.md` | No-K exact output and first-blocker are not claimed as novel |
| Semantic sufficiency boundary | `plan/research/semantic-stopping-neighbors.md` | Exact-prefix certification is not claimed to decide answer sufficiency |
| Publication decision | `plan/research/paper-path-decision.md` | Chinese synthesis and decision matrix agree |

## Red-team questions

1. **Can the method be sold as parameter-free?** No.  It removes requested K
   from the retriever interface but still requires a resource or risk contract.
2. **Can first-blocker be sold as new?** No.  Its action principle is a WRRF
   specialization of Selective NRA/SNRA.
3. **Can the replay be sold as a latency result?** No.  Current Dense setup
   evaluates every quantized row before the logical cursor advances.
4. **Can set-safe certification carry a standalone paper?** Not on present
   evidence.  It is useful but established and still K-dependent.
5. **Is there a credible high-upside route?** Yes, conditionally: a materially
   tighter aggregate exact-MIPS index with real time-to-prefix gains, or a new
   calibrated-risk semantic project with independent data and baselines.

## Disposition

No unresolved numerical or terminology conflict was found in the final
synthesis.  The research question has a defensible negative answer for the
cheap rank-only formulation and explicit reopening gates for the two larger
alternatives.
