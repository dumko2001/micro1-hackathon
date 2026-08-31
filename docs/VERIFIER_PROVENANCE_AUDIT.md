# Verifier provenance and case audit

Snapshot: 30 August 2026. This is author/reviewer context, not agent input. It
separates requirements available at task time from private oracle reasoning.

## Rule

A verifier may require an internal symbol or data contract only when it existed
in the clean parent or is a mechanical extension of an established Prometheus
convention. A public issue symptom, reproducer, or reviewed external interface
may be stated in the instruction. Oracle-invented helper names, patch structure,
target files, hidden cases, and private root-cause reasoning are not agent
requirements. Reviewed architectural invariants may be enforced when the task
is explicitly upstream-conformance, but the verifier must record why they
matter.

The visible instruction states the incident and any new public
interface. It does not enumerate routine senior-maintainer obligations such as
preserving established behavior, failing safely, maintaining compatibility, or
covering the repository's normal lifecycle paths. The verifier may enforce
those obligations when they follow from the clean repository and established
Prometheus conventions. This suite deliberately adds two stricter conformance
choices: the reviewed PromQL preprocessing boundary and the landed ST wire
format. They are documented here and in task metadata, not leaked as solution
steps in the actor instruction.

## Unix-socket scraping

This is an explicitly compound corrected-feature episode: #18091 adds the
public `__unix_socket__` target contract and #19399 corrects transport pooling.
It is not represented as the exact knowledge state of one author on one parent.

- Fair visible contract: literal relabel label; HTTP/HTTPS; advertised Host and
  TLS identity; target isolation; reload/resync; fail closed; ordinary TCP.
- Not fair to require: `UnixSocketLabel`, `newUnixSocketScrapeClient`, a context
  key type, a per-target cache name, or the oracle's client layout.
- Positive cases: HTTP UDS, HTTPS UDS, empty address mapped to `localhost`, two
  targets on one socket sharing an effective pool, two sockets sharing an
  authority remaining isolated, UDS and TCP sharing an authority remaining
  isolated, socket change after reload/resync, ordinary TCP, and keep-alive
  reuse.
- Negative cases: after reload, a nonexistent socket may be omitted or report
  `up=0`; in either case a live TCP trap must record no fallback connection.
- Boundary: an external controller drives a candidate daemon through
  randomized HTTP and TLS sockets. It uses the literal public label and imports
  no Oracle-invented production symbol.

## Step-invariant subquery semantics

This is the exact #18610 reproduction implemented by #19187. The public report
included the failing query shape; the internal AST diagnosis remains hidden.

- Fair visible contract: the reported fixed-time subquery symptom plus correct
  instant/range, nested, `@`, offset, and ordinary-subquery behavior.
- Required reviewed invariant: the subquery node itself remains step-sensitive
  while invariant work inside it may still be wrapped. The verifier does not
  require the Oracle helper or source diff.
- Positive cases: fixed-time matrix and subquery forms, constant and
  step-varying arguments, nested expression, `@ start()`, `@ end()`, and offset.
- Negative/regression cases: ordinary non-fixed subqueries must remain
  step-varying and fixed constant results must remain invariant.
- Boundary: an external controller queries a candidate daemon over HTTP.
  A verifier-owned probe checks the exported preprocessed AST without naming a
  private helper.

## Native-histogram extended rates

This is an explicitly compound corrected-feature episode: #18564 adds native
histogram support and #18943 removes its direct mixed-window panic. The prompt
reports the public bare-versus-wrapped symptom but not the internal cause.

- Fair visible contract: anchored/smoothed `rate`, `increase`, `delta`, pure
  smoothed selectors, reset behavior, schema compatibility, warnings, and no
  panic.
- Not fair to require: interpolation helper names, reset-correction helper
  structure, or the reference evaluator decomposition.
- Positive cases: anchored and smoothed rate/increase/delta, pure selector
  interpolation and exact sample, exponential and custom-only histograms,
  compatible schema reduction, boundary resets, range evaluation, and floats.
- Negative cases: incompatible exponential/custom schemas and mixed
  float/histogram windows return normal warnings with no result or panic.
- Boundary: a daemon/API controller checks PromQL output and annotations. A
  conjunctive linked Go test adds interpolation and reset breadth, so this task
  retains a hostile-candidate limitation.

## Start-timestamp persistence

The public proposal and #18609 define a long-horizon storage feature. Existing
`AppenderV2.Append`, `Iterator.AtST`, `EnableSTStorage`, chunk interfaces, and
parallel encoding/type naming conventions make the new public encodings and
`histograms-st-encoding` feature flag legitimate contracts. The final task also
treats the landed persistent byte format as an upstream-conformance contract.

- Fair visible contract: integer and float histogram start timestamps across
  head, OOO, WAL/WBL, compaction, block reopen, and queries; legacy behavior
  when disabled; independent histogram-ST and XOR2 feature gates.
- Convention-fair internal surface: parallel chunk encoding/type names and the
  established command feature parser/options path.
- Not required: private `stEncoder`/`stDecoder` names, setter organization, or
  source layout. Required: blocks must interoperate with the exact landed
  reader, which indirectly fixes the reviewed header and sample grammar.
- Positive cases: 130-sample semantic receipts across seek, recode, chunk cuts,
  compatible layout expansion, zero-threshold transition, stale recovery,
  normal and OOO storage, WAL/WBL replay, block reopen, and all four feature-flag
  combinations.
- Negative/regression cases: feature-off legacy encodings, `AtST()==0`, V1 WAL
  compatibility, failed append immutability, stale markers, and seek past end.
- Boundary: writer and reader programs compiled from candidate source exercise
  normal and OOO storage through pre-existing query and iterator APIs. A
  root controller projects valid blocks into a root-owned read-only tree,
  deletes the original writable database, seals the parent, and compares
  receipts for every sample. A clean-parent writer creates legacy integer and
  float fixtures. A second root-only reader built from the landed patch must
  decode the same sealed blocks and return identical receipts.
- Boundary: the candidate cannot read the landed source or reader binary. The
  gate checks wire interoperability without requiring the Oracle's Go names or
  call graph.

## Stale-series WAL expiry

The clean parent already contains `walExpiries`, its time-domain comment,
checkpoint predicates, truncation, and stale compaction lifecycle. Enforcing
that existing retention mechanism is repository-convention conformance, not an
oracle-invented method constraint. The two-line unit mismatch diagnosis remains
hidden.

- Fair visible contract: keep evicted-series metadata exactly while WAL records
  reference it, expire after the sample horizon, avoid replay warnings, preserve
  unrelated active series.
- Positive cases: pre-horizon checkpoint retention, reopen/replay, zero unknown
  references across record kinds, active-series survival.
- Negative cases: post-horizon checkpoint omission, no stale resurrection,
  expiry bookkeeping deletion, active control retained.
- Boundary: a candidate program writes WAL checkpoints. A trusted
  clean-parent reader checks membership and replay behavior across randomized
  horizons, with pre-existing retention assertions as supporting evidence.

## Evidence status

The five current packages pass deterministic materialization, shell/Python
syntax, Harbor 0.14 task parsing, and source checksums. On the current
Oracle-conformance bytes, frozen Daytona evidence contains five Oracle rewards
of `1`, five no-op rewards of `0`, five accepted alternates, and ten rejected
mutants, all without Harbor exceptions. Two formerly accepted non-landed ST
encodings also return `0`. The older 30-case full gate and 20-case repeat gate
remain bound to earlier bytes and are not current-byte repeatability evidence.

These results certify the registered candidates, not every valid architecture.
The start-timestamp verifier briefly accepted alternate encodings, then moved
back to exact landed-format interoperability when the task policy changed from
method neutrality to upstream conformance. Two formerly passing Luna-max
archives now return reward `0`; the exact reference and an independently
organized format-compatible alternate return `1`.

Histogram retains a linked breadth test; start timestamp no longer runs reward
assertions in a process linked with candidate code. Neither boundary proves
resistance to deliberately task-aware code. Earlier ST solve rates belong to
the superseded method-neutral verifier and are not final conformance results.

The verifier runs separately without network access. Daytona Codex actors need
public egress for the model service. Opaque identifiers and the instruction not
to search for online solutions can add friction, but neither proves that an
actor cannot identify upstream code or search the web.
