# Review pass 4: anytime results and claims

- Recomputed the pooled rows directly from the per-query CSV.
- Confirmed total work equals Dense plus Sparse depth for every saved state.
- Confirmed first-blocker grid regret is zero in all 776 primary states and all
  776 chunk-64 robustness states.
- Confirmed boundary-pressure has regret one in four primary states.
- Confirmed balanced is below the grid envelope in 281 primary states.
- Confirmed the two poison-query trajectories from per-query rows.
- Restricted all efficiency statements to logical access depth; no wall-clock
  or live latency claim is made.
- Restricted all optimality wording to the evaluated allocation grid and two
  frozen TREC-DL query sets.

Result: reported directions and headline values are supported by saved rows.
