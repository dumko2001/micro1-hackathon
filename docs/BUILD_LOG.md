# Build log

This is the technical trace behind the shorter [Improvement changelog](../CHANGELOG.md). Failed experiments stay visible, and host checks remain separate from Daytona evidence.

## 29 August: first task

- Selected fixed-time PromQL subqueries because the public reproducer has deterministic instant and range outputs.
- Pinned clean parent `38c29bc2e26f6fe52d347c6d325552cf68810454` and merge `68119c094875452839d34d259b7394d0176cb844`.
- Recorded clean-parent archive SHA-256 `218bec9b497ea44d5aad97b86e5c5a598bba50999020b4af5c9492ae01d5b334`.
- Moved the environment to pinned Go 1.26 after dependency validation showed Go 1.25.8 was too old for the locked module graph.
- Measured a first focused host test at 142.91 seconds, a first broad Prometheus build at 215.33 seconds, and a warm rebuild at 23.08 seconds.
- On the same semantic cases, the parent failed five fixed-time assertions and the exact PR passed all cases.

At this point the project had one runnable task and host behavior evidence. It did not have a calibrated suite.

## 29 August: five-task family

- Added separate historical parents, archive hashes, reference stacks, prompts, budgets, and verifiers for UDS scraping, native-histogram rates, histogram start timestamps, and stale-series WAL expiry.
- Generalized the materializer to validate archives, reject links and special entries, generate through a temporary directory, and replace destinations atomically.
- Switched the actor to non-root execution and hardened collection around a root-owned artifact handoff.
- Rejected PR #18091 alone after two Unix sockets with one advertised authority returned the wrong series. Added direct pooling correction #19399.
- Rejected PR #18564 alone after a mixed smoothed window still panicked. Added direct correction #18943.
- Reclassified #18609 as a 34-file storage-format feature. Excluded later #19201/#19202 behavior.
- Removed candidate tests from reward truth, restored trusted harness files, and replaced candidate-controlled PromQL helpers.
- Added transport traps, schema/reset cases, split WAL lifecycles, independent feature flags, OOO storage, restart, and block-reopen checks.

This phase proved clean-parent failure and exact-reference success. It still relied too heavily on linked Go verifier tests.

## 30 August: trust-boundary rewrite

- Replaced the UDS linked test with a root controller driving a candidate Prometheus daemon through randomized HTTP and TLS Unix sockets.
- Replaced the step linked test with a root controller driving instant and range queries against a candidate daemon and trusted backfilled data.
- Made WAL expiry a candidate-program/trusted-reader protocol over candidate-generated checkpoints.
- Added an external daemon/API controller to the histogram task and an external artifact gate to start timestamps.
- Kept a linked supplemental test only for histogram reset/interpolation behavior that has no stable external interface.
- Ran candidate executables as UID 65532 with an empty environment, no capabilities, `no_new_privs`, and resource limits. Deleted build sources before execution.
- Git-stripped all actor archives and removed source provenance, solutions, comments, and verifier material from the actor boundary.

## 30 August: Daytona corrections

The first diagnostic run exposed three harness defects rather than product defects:

- an invalid assumption that a Daytona no-network sandbox exposes only a loopback interface;
- parallel Go compiler memory pressure under the authorized 4 GiB limit;
- generated start-timestamp controller code that used its database handle before declaration.

The final launcher trusts Daytona's network policy, compiles serially with `GOMAXPROCS=2`, `CGO_ENABLED=0`, and `-p=1`, and fixes the declaration order. The failed diagnostic is retained but not cited as certification evidence.

## 30 August: candidate calibration

- Relaxed one UDS false reject: after a configuration reload, a missing socket may be omitted or remain visible with `up=0`. Both are fail-closed only if the live TCP trap stays untouched. Corrected the acceptance rule and reran the task's final matrix.
- A stock step trajectory completed a verifier-passing patch but reached the 1800-second actor timeout. Raised the final actor budget to 3600 seconds and recertified that task's candidate matrix.
- Documented the histogram controller's `1e-12` relative tolerance after review flagged the missing rationale. Repeated the task's final-byte matrix after the metadata change.
- Removed Go-generated `go.work.sum` before start-timestamp collection so a build byproduct cannot alter candidate identity. Repeated its final-byte matrix.
- Replaced start-timestamp's remaining concrete-type tests with external candidate writer and reader programs. The corpus checks receipts for 130 samples across recode, chunk threshold, stale recovery, restart, compaction, and fresh `Seek`.
- Tested a method-neutral ST reader after clean stock implementations chose coherent encodings that differed from the Oracle. This was retained as development evidence, then superseded when the task was explicitly changed to landed-format conformance.
- Made the start-timestamp root controller project valid blocks into a root-owned read-only tree, delete the writable database, and seal its parent before candidate reads. A clean-parent writer supplies legacy fixtures, and only the root controller computes expected receipts.
- On the earlier method-neutral package, two exact-reference and two no-op decisions per task returned 10 rewards of `1` and 10 rewards of `0`; fifteen named mutants returned `0`, and five alternates returned `1`.
- The histogram false reject came from treating an incompatible first sample as a reset and dropping it. An independent bucket-family compatibility preflight now rejects that window while accepting the alternate.
- Added a root-only reader built from the exact landed ST patch. It reads the same sealed candidate blocks and must return the same receipts as the candidate reader. The registered alternate still passes because it preserves the final format.
- The earlier private 30-case and 20-case gates each reported balanced accuracy `1.0`, false-accept rate `0.0`, and false-reject rate `0.0` on their pinned bytes.
- On the current Oracle-conformance bytes, the exact references passed 5/5, no-ops failed 5/5, format-compatible alternates passed 5/5, and two mutants per task failed 10/10. Two formerly accepted ST encodings also failed the landed-reader gate. All trials ended without Harbor exceptions.
- Bound those 25 current decisions in `oracle-conformance-manifest.json`. The native Harbor evidence gate reports balanced accuracy `1.0`, false-accept rate `0.0`, and false-reject rate `0.0`.

Exact task hashes, job names, timings, candidate defects, and verifier boundaries are in [the evidence ledger](TASK_SUITE_EVIDENCE.md).

## Model evidence

On earlier verifier bytes, ten `gpt-5.6-luna` max-reasoning runs produced eight passes. UDS, step, WAL, and start timestamp passed twice; histogram missed required semantics twice. The two start-timestamp candidates used different encodings and passed the neutral verifier, but both now fail the landed-format gate.

The final packages then received two completed `gpt-5.6-luna` runs per task with no reasoning override; Harbor used its default `high` setting. WAL passed twice. Both UDS candidates omitted the established `localhost` authority for an empty advertised address. Both subquery candidates implemented downstream unwrapping instead of preserving the reviewed preprocessing boundary. The histogram candidates missed reset/interpolation semantics. The ST candidates implemented coherent non-landed formats: one used an extra-header organization and one used a sidecar presence bitmap. The final result is 2/10 with no exceptions, 93,842,853 input tokens, 91,727,360 cached input tokens, 278,327 output tokens, $2.59163820, 3:15:24.21 summed trial wall time, 2:13:57.51 agent time, and 52:01.56 verifier time.

The original combined coordinator wrote eight terminal results before stopping with one UDS and one ST trial marked active. The UDS actor had finished but never received a reward; the ST actor had not produced a trajectory. Isolated replacement jobs produced the two missing terminal rewards. The incomplete trials are disclosed and excluded, not relabeled as behavioral failures.
