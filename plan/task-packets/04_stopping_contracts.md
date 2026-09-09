# Task Packet: stopping and request contracts

- Scope: Enumerate and analyze alternatives to fixed depth and fixed K for an
  online exact hybrid-fusion API.
- Files to read: `plan/project-overview.md`, `plan/experiment-protocol.md`,
  `results/poison-case-analysis.md`, `results/anytime-frontier-analysis.md`.
- Files allowed to edit: `plan/research/stopping-contracts.md` only.
- Required skills: experiment-results-planning.
- Evidence/data inputs: current frozen replay results and any directly relevant
  verified literature.
- Required artifacts: formal definition, observable state, stopping rule,
  required parameter, guarantee, operational interpretation, failure mode, and
  replayability for each candidate contract. Include fixed logical work,
  cost-weighted work, wall-clock deadline, certification-gap threshold,
  marginal certified-prefix gain, risk-limited approximation, downstream
  context/token budget, and parameter-free/Pareto-frontier interfaces.
- Rejection checks: do not call a rule parameter-free when it hides a deadline,
  tolerance, utility model, or system limit; do not use qrels in a deployable
  stopping decision; separate exactness from semantic sufficiency.
- Validation: recommend at most three contracts for experiment and state why
  the others should be rejected.

