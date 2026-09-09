# Reduction audit: complete-list WRRF as classical ranked-input aggregation

## Result

The fusion problem is a direct instance of sorted-access-only monotone rank
aggregation. LARA-IN therefore preempts the output-interface contribution, and
Selective NRA (SNRA) preempts the pilot's strongest-competitor/first-blocker
action. The remaining research object, if any, is the objective and guarantee
under arbitrary interruption and heterogeneous cost—not the ability to
enumerate exact fused results or the local blocker rule.

## Mapping

Let the document universe be \(\mathcal D\) and let channel \(c\) expose a
ranked stream \(\pi_c\). Define its atomic score for document \(x\) as

\[
s_c(x)=
\begin{cases}
\dfrac{w_c}{\kappa+r_c(x)}, & x\text{ occurs in }\pi_c,\\
0, & x\text{ is absent from a finite-support channel}.
\end{cases}
\]

Because \(w_c\ge 0\) and reciprocal rank decreases with \(r_c\), each stream is
already sorted by non-increasing atomic score. Complete-list WRRF is

\[
F(x)=\sum_c s_c(x),
\]

which is the monotone `sum` aggregate used by NRA/LARA. No keyed random access
is required: after sorted prefixes \(d_c\), an identity already seen in some
channels has the usual partial lower bound and receives
\(w_c/(\kappa+d_c+1)\) as its missing-channel upper contribution. A wholly
unseen identity receives the sum of the next-unread contributions. When a
finite positive-score stream is exhausted, its missing contribution becomes
zero.

Successive LARA-IN `GetNext()` outputs and the current project's longest
certified ordered prefix describe the same semantic object. The implementation
here may certify several consecutive objects at one observed state, whereas
`GetNext()` exposes them one at a time; this is an API granularity difference,
not a new ranking guarantee.

## Assumptions that hold

- Atomic scores are non-negative and each channel is sorted by them.
- The aggregate is monotone and subset-decomposable (`sum`).
- Channel identities can be joined by a stable document identifier.
- Sorted access can be resumed while an available prefix remains.
- Sparse zero-score absence is compatible with an exhausted finite-support
  stream whose remaining contribution is zero.

## Assumptions and engineering details that need explicit handling

1. **Stable ties.** Classical statements often specify only non-increasing
   aggregate score. The implementation defines a total order by aggregate score
   and stable point identity. Every lower/upper comparison must therefore
   include this secondary key. It can be viewed as a lexicographic order rather
   than an unsafe floating-point perturbation.
2. **Stored prefix versus exhaustion.** A 5,000-entry artifact is not an
   exhausted stream merely because no more ranks were saved. Its unread bound
   remains the rank-5,001 contribution and results that need deeper evidence
   are censored. By contrast, NFCorpus Dense reaches its full corpus size and a
   Sparse positive-support list shorter than the requested cap is exhausted.
3. **Zero Sparse scores.** Documents outside the positive Sparse support all
   contribute exactly zero. They need not be enumerated in an arbitrary tie
   order after support exhaustion, because Dense supplies their identities and
   Sparse cannot change their fused scores.
4. **Floating-point semantics.** Exactness means exact agreement with the
   declared implementation's score precision and tie rule, not equality over
   real arithmetic. The exhaustive reference and certificate must share those
   semantics.
5. **Opaque engine costs.** Classical access counts do not establish that one
   Dense continuation and one Sparse continuation have equal wall-clock,
   monetary, or energy cost.

## What remains different enough to study

LARA-IN establishes how to emit the next exact aggregate answer and permits an
arbitrary input access schedule. SNRA goes further: it identifies the viable
non-result with the largest upper bound and selectively accesses that object's
missing fields. For two WRRF streams, this is the same action as the pilot's
first-blocker rule. This project can therefore ask only the narrower question:
does optimizing certified-prefix yield over an unknown interruption frontier,
especially under heterogeneous Dense/Sparse continuation costs, require a new
policy or guarantee beyond fixed-$k$ SNRA/HSNRA?

That distinction is only publishable if it survives direct classical
baselines. Required comparators are round-robin LARA-IN/NRA, SNRA/HSNRA,
largest-next-bound descent, J*-style next-answer routing, Upper/IO-style
cost-aware scheduling, and known-budget Best-Effort-style policies. The no-`K`
interface and strongest-competitor action must both be credited to prior work.

## Primary evidence

- Mamoulis et al., *Efficient Aggregation of Ranked Inputs*, ICDE 2006,
  Section 5.2: LARA-IN is sorted-access-only, stateful, exact, and operates
  “without a constraint k.” DOI: <https://doi.org/10.1109/ICDE.2006.54>;
  author PDF: <https://www.cs.uoi.gr/~nikos/icde06_lara.pdf>.
- Fagin, Lotem, and Naor, *Optimal Aggregation Algorithms for Middleware*,
  JCSS 2003. DOI: <https://doi.org/10.1016/S0022-0000(03)00026-6>.
- Cormack, Clarke, and Buettcher, *Reciprocal Rank Fusion Outperforms Condorcet
  and Individual Rank Learning Methods*, SIGIR 2009. DOI:
  <https://doi.org/10.1145/1571941.1572114>.
- Yuan et al., *Efficient processing of top-k queries: selective NRA
  algorithms*, Journal of Intelligent Information Systems 39(3), 2012,
  DOI: <https://doi.org/10.1007/s10844-012-0208-5>; conference precursor:
  <https://doi.org/10.1007/978-3-642-00672-2_4>.
