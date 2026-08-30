# Storage task epistemics and verifier boundary audit

## Scope and lineage

The task source archives are the clean first parents recorded in each task's private provenance file. The solution patches are the exact landed upstream changes and serve only as Oracle candidates. Reward does not compare candidate source to either patch.

### Stale-series WAL expiry

The clean parent already contains all of the relevant contract vocabulary:

- `walExpiries` is documented as the time until which removed-series metadata must remain.
- `updateWALExpiry` stores the greater timestamp under the existing lock.
- `keepSeriesInWALCheckpointFn` retains a missing series when `keepUntil >= mint`.
- `truncateWAL` removes bookkeeping only when `keepUntil < mint`.
- `gcStaleSeries` receives the removed series' maximum sample timestamp.

The defect is local and mechanically identifiable in the clean parent: `gcStaleSeries` writes a WAL segment number into this timestamp-domain map. The landed patch changes that value to `maxt`. The verifier's internal reads of `getWALExpiry`, checkpoint creation, and replay metrics therefore enforce pre-existing Prometheus contracts rather than Oracle-invented identifiers.

The alternate candidate uses the already-established `updateWALExpiry` helper and should pass despite differing from the landed patch. Named mutants cover the original unit mismatch, an exclusive rather than inclusive expiry boundary, and permanent over-retention.

### Histogram start-timestamp persistence

The clean parent already has the generic start-timestamp and storage conventions: iterator `AtST`, start-timestamp append APIs, WAL/WBL start-timestamp records, the `st-storage` gate, the XOR2 float encoding, encoding registration/pooling, head and out-of-order chunk creation, block reopen, and PromQL start-timestamp behavior.

The following are genuinely new in the landed feature rather than inferable names from the clean parent:

- the two histogram start-timestamp encoding identifiers and concrete Go types;
- their exact on-disk byte layouts;
- the internal histogram-encoding option fields and propagation names.

The public `histograms-st-encoding` feature name and its independence from `xor2-encoding` are stated in the task contract. Reward does not compile upstream tests that instantiate the landed concrete Go types or call their exact method signatures, and it does not use the landed decoder. The controller discovers the effective option behaviorally. A writer and a separate reader compiled from candidate code must preserve complete histogram semantics across WAL/WBL restart and block-only reads after compaction. A clean-parent writer independently creates legacy integer and float block artifacts, which the candidate reader must recover exactly. Internal names, organization, encoding identities, and the landed byte layout are not graded.

This is intentionally weaker than an independent byte-interoperability claim. The candidate writer and reader share candidate code and could collude if they recognized the hidden protocol. The verifier therefore establishes lifecycle behavior for honest implementations and clean-parent backward readability, not a formal proof that arbitrary third-party readers can decode candidate-written bytes.

Named mutants cover accidental coupling of the two feature flags, failure to select the ST-capable formats during OOO chunk conversion, and integer-histogram corruption during compatible layout recoding.

## Separate verifier and hostile-code boundary

Both task manifests use Harbor `environment_mode = "separate"`. The agent container never receives the verifier image. Collection kills remaining agent-UID processes, makes the candidate tree immutable, and exports a checksum-pinned regular-file-only archive. The verifier then:

1. validates archive paths, entry types, expansion limits, and checksum;
2. restores the clean parent's module metadata and every upstream test file;
3. injects verifier-owned programs and cases and compiles with workspace/vendor overrides rejected and cgo disabled;
4. builds root-owned candidate programs, a clean-parent legacy writer, and the controller;
5. deletes candidate source before execution and makes verifier assets root-only;
6. runs each candidate program as UID 65532 with an empty environment, no capabilities, `no-new-privileges`, and resource limits inside the provider-enforced no-network verifier environment;
7. has the root-owned controller compare complete receipts from a separate candidate-linked reader and clean-parent-generated legacy artifacts.

For WAL expiry, the candidate program creates randomized real checkpoints through exported TSDB APIs; a clean-parent reader independently decodes their series records and the controller checks inclusion at the exact boundary and exclusion one millisecond later. For histogram persistence, the candidate program discovers the independently effective histogram option through behavior rather than a new symbol name, performs integer and float histogram WAL/WBL restart plus normal/OOO compaction, and leaves TSDB artifacts. The controller projects only valid block directories, excluding WAL, WBL, and head chunks, before the candidate reader opens the result read-only. The corpus includes mixed start timestamps, more than 127 samples, compatible within-series layout expansion, a zero-threshold chunk transition, stale markers followed by normal recovery, complete ordered iteration, fresh in-range `Seek`, and past-end `Seek`. Canonical receipts cover start timestamp, timestamp, kind, reset state, schema, zero threshold and count, nonzero bucket populations, custom bounds, count, and sum. Equivalent span segmentation is accepted. The clean-parent legacy writer creates root-owned, read-only integer and float block artifacts; the candidate reader must recover those with zero start timestamps.

Reward does not run assertions in a Go test process linked with candidate code. Candidate binaries run as UID 65532, are killed after each invocation, and cannot read the root-owned controller or legacy artifacts. The external process boundary closes the prior proof-token/file-descriptor escape. It is still not a formal proof against a deliberately task-aware candidate writer and reader that recognize and jointly fabricate the randomized protocol.

## Current calibration status

The exact landed patch passed the final process-separated, method-neutral host controller twice after block-only projection, complete iteration, past-end `Seek`, clean-parent legacy generation, recode, threshold, and stale-recovery checks. The saved R2 alternate also compiled and passed that controller once. The saved R1 writer and reader compiled, but its Prometheus binary could not be rebuilt because the host ran out of disk; R1 therefore has no result against this verifier. No Daytona run has yet exercised this final verifier. Earlier Daytona Oracle/no-op/alternate/mutant results belong to the superseded exact-decoder verifier and are not current release evidence. Mutant fixtures and the no-op still require fresh recalibration against the final materialized task.
