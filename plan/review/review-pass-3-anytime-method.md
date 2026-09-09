# Review pass 3: anytime method and exactness

- Checked unequal-depth upper bounds separately for unread Dense and Sparse
  contributions.
- Checked the anonymous unseen-object bound and the upper bounds of objects seen
  in only one channel.
- Checked stable point-identity tie handling against the frozen exhaustive WRRF
  order.
- Confirmed that the deployable schedulers use only current ranks and bounds;
  neither qrels nor future ranks influence allocation.
- Confirmed that the reporting cap of 100 is not read by a scheduler and is used
  only because the frozen exhaustive oracle ends at Top-100/101.
- Rejected the statement that the method is wholly parameter-free: finite
  interruption still requires an external work/deadline or utility preference.
- Renamed the analysis envelope from “allocation oracle” to “allocation grid
  oracle” to prevent a continuous-space optimality overclaim.

Result: no unresolved exactness defect found.
