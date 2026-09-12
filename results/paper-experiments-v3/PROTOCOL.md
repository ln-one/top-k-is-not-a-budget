# Static ranking protocol

The five static query sets use complete reconstructed channel rankings. Dense
scores use the frozen ARM64 float32 normalization and dot-product arithmetic.
Sparse scores accumulate in ascending original term-ID order and retain positive
support. Equal raw scores use stable UUID order.

Full-list RRF references are computed independently. Both schedules share the
certifier, budgets, and unit/batch-64 access granularity. Every trajectory continues
until Top-20 is certified; budget endpoints are also recorded up to 100 outputs.
All emitted states are checked against the array certifier, and nDCG is checked
with pytrec_eval. No reconstructed tail is attached to an old prefix.

Temporal snapshots retain their original frozen rankings because some source
shards are unavailable. Their results remain separate.
