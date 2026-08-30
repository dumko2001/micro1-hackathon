# Task suite evidence ledger

Snapshot: 30 August 2026. Static provenance, host checks, Daytona execution, private evidence binding, and model difficulty are separate evidence classes.

## Registered lineage

| Task | Clean first parent | Reference commit(s) | Source SHA-256 |
|---|---|---|---|
| Unix-socket scraping | `92aa2e73df04594bd941dd9b6f073cf27e320820` | `c5fa89db085c9b3855d7916f2ade047066a7a318` + `05f9eb8b3b8e10b48c8f4153b0714dbe9bc9a630` | `3f014fbedbdecbd18207b01e9deabba6a393bdb01e32765f64cab65fdfc2aff0` |
| Step-invariant subquery | `38c29bc2e26f6fe52d347c6d325552cf68810454` | `68119c094875452839d34d259b7394d0176cb844` | `218bec9b497ea44d5aad97b86e5c5a598bba50999020b4af5c9492ae01d5b334` |
| Native-histogram rates | `cb085a6281e242e4694306901b7931e5801e5387` | `06b569ae2a6e43d08490370e10f0df8c7ba0fb68` + `2626a65a8282703f1378e341565922756a4a0f9a` | `9683e773587c96fa1e396cd83e53985fcd408789b964b7aab03f30e47d7be951` |
| Start-timestamp persistence | `12be92b1171fb6cabf01ea292939aa17d06b6c09` | `abb5a2f9471a7315cbd9562087412340b2825ccb` | `3d7da00af107e9979a0769da59410b9fade61aa8ebc5920d7ed71315b652f906` |
| Stale-series WAL expiry | `05d9bd4a2789196c1361acfe06a2edf79440d8c0` | `5ddb7e49e3c89c406687cf020f85e04a3bac16fd` | `ed12931b2819c6159f50eb24960e78f505a4bdf32974a3717305c809d8019929` |

All source archives pass their SHA-256 checks. Every upstream patch stack applies in order to its clean parent. Actor archives contain no Git history or solution material.

## Current Harbor task digests

| Task | Harbor task checksum | Files |
|---|---|---:|
| Unix-socket scraping | `81ae9884f2e0c99d7d67c63adba7059c655e8946eebb20d7a2af43f41db701e0` | 20 |
| Step-invariant subquery | `942d83d397e25a26c606b86c59d7a2c83dc4158040446f178a59764df2946e93` | 19 |
| Native-histogram rates | `4cb916e104943c0056820052dde5760083e7bcb89090e7a745c7b5acd6152683` | 20 |
| Start-timestamp persistence | `484b625cda23135c577bbcde198415a4bb7aea7af6df74a3df0be728c70817d4` | 22 |
| Stale-series WAL expiry | `485bb43bedc0762ad1b2619b66cff5f71ef9b78ad39b7604a4e5ff0bb73d19a1` | 21 |

Verify mode, Harbor parsing, source parity, and no-`.git` checks pass on these packages. The current jobs below record the same checksum in each trial result.

## Task shape and verifier boundary

| Task | Shared episode shape | Unique verifier observation | Remaining limitation |
|---|---|---|---|
| Unix-socket scraping | clean parent, non-root actor, separate verifier | live randomized HTTP/TLS sockets plus pool-identity, keep-alive, reload, localhost, TCP isolation, and fallback gates | actor egress makes the no-search rule a policy control |
| Step-invariant subquery | same | instant/range API results plus the reviewed direct-subquery AST boundary | deliberately rejects downstream-unwrapping workarounds |
| Native-histogram rates | same | daemon/API output, warnings, resets, schemas, panic resistance, and linked interpolation breadth | candidate code shares a process for the linked breadth test |
| Start-timestamp persistence | same | candidate and landed-format readers compare complete receipts from root-owned sealed blocks; clean-parent writer supplies legacy fixtures | final wire-format interoperability is intentionally enforced |
| Stale-series WAL expiry | same | clean-parent reader checks checkpoint membership and queries retained compacted and active data across randomized horizons | pre-existing internal retention conventions are intentionally enforced |

Candidate programs run as UID 65532 with an empty environment, `no_new_privs`, no capabilities, and resource limits. Build sources are removed before executable gates run. These controls reduce the tested attack surface. They do not prove safety against arbitrary hostile code.

## Current Daytona results

Harbor used Daytona only. Every sandbox requested 2 vCPU, 4096 MiB RAM, and 10240 MiB disk, with at most five concurrent sandboxes.

| Case class | Jobs | Decisions | Result | Exceptions |
|---|---|---:|---:|---:|
| Exact reference | `micro1-oracle-alignment-final-oracle-20260830`; ST rebound by `st-oracle-conformance-final-oracle-20260830` | 5 | 5 reward `1` | 0 |
| No-op | `micro1-oracle-alignment-final-nop-20260830`; ST rebound by `st-oracle-conformance-final-nop-20260830` | 5 | 5 reward `0` | 0 |
| Alternate-valid | `micro1-oracle-alignment-final-alternate-main-20260830`; UDS and ST rebound separately | 5 | 5 reward `1` | 0 |
| Mutant 1 | `micro1-oracle-alignment-final-mutant-1-20260830`; ST rebound separately | 5 | 5 reward `0` | 0 |
| Mutant 2 | `micro1-oracle-alignment-final-mutant-2-20260830`; ST rebound separately | 5 | 5 reward `0` | 0 |
| Formerly passing ST encodings | `st-oracle-conformance-replay-max-r1-20260830`; `...max-r2...` | 2 | 2 reward `0` | 0 |

This is one final-byte decision per registered case, not a repeatability estimate. Earlier task digests have 2-run reference/no-op evidence and five additional ST mutants; those remain development history until replayed on this final package.

## Alternate-valid and mutant calibration

The UDS alternate uses a different registry and ownership layout. Step uses a different wrapper guard. Histogram normalizes the window and checks bucket families independently. WAL factors expiry through another helper path. The start-timestamp alternate reorganizes dispatch but keeps the landed persistent format.

| Task | Mutant 1 | Mutant 2 | Additional start-timestamp mutants |
|---|---|---|---|
| Unix-socket scraping | cross-target pooling | TCP fallback | — |
| Step-invariant subquery | wrong wrapping boundary | `start()`/`end()`-only fix | — |
| Native-histogram rates | partial mixed-window/panic fix | reset interpolation defect | — |
| Start-timestamp persistence | feature flags coupled | OOO encoding downgrade | recode loss; always-on persistence; block loss/read repair; stale-recovery defect; `Seek` defect |
| Stale-series WAL expiry | off-by-one lifetime | retain forever | — |

The start-timestamp corpus has 130 samples. It crosses recode and chunk thresholds, expands compatible bucket layouts, changes zero thresholds, recovers from stale markers, reopens WAL/WBL and normal/OOO blocks, and exercises fresh and past-end `Seek`. The root controller compares timestamp, start timestamp, kind, reset state, schema, zero threshold and count, bucket populations, custom bounds, count, sum, ordering, and cardinality. Equivalent span segmentation is accepted.

## Start-timestamp conformance decision

The project tested a method-neutral version first. It built both writer and reader from candidate source and accepted two clean Luna-max solutions with different on-disk formats. That experiment showed the lifecycle could be solved without reproducing the landed bytes.

The final task is stricter by design. It treats the reviewed persistent format as part of upstream conformance. The candidate writer still creates real normal and OOO lifecycles, and its own reader must return complete semantic receipts. The controller then runs a second root-only reader built from the exact landed patch against the same sealed blocks. Both readers must agree. The Oracle source and reader are inaccessible to the candidate process.

The two formerly passing Luna-max archives now return reward `0`. The registered ST alternate still returns `1` because it changes dispatch organization while preserving the final format. This is deliberate format conformance, not a claim of method neutrality.

## Private evidence gates

The private grader binds task digest, candidate identity, agent, resource request, artifact hash, verifier status, reward, and job ID. It rejects missing or extra cases, path escapes, links, mismatched rewards, and infrastructure states.

| Gate | Decisions | Complete | Balanced accuracy | False accepts | False rejects |
|---|---:|---:|---:|---:|---:|
| Full: reference, no-op, alternate, and mutants | 30 | yes | `1.0` | `0.0` | `0.0` |
| Repeatability: reference r1/r2 and no-op r1/r2 | 20 | yes | `1.0` | `0.0` | `0.0` |

These metrics apply only to the registered candidates and pinned jobs. The repository now includes the reviewer fixtures and reports; raw `jobs/` output and credentials remain ignored. A public copy is therefore a transparent benchmark artifact, not a secret evaluator.

## Failed experiments kept in the record

- An early diagnostic treated every non-loopback interface as a network-policy failure. Daytona still exposes an interface in the verifier sandbox. The final gate relies on the backend network policy and tests application behavior.
- Parallel Go compilation exceeded the 4 GiB limit. Final builds use `GOMAXPROCS=2`, `CGO_ENABLED=0`, `-p=1`, and serialized compilation.
- A generated start-timestamp controller referenced its database handle before declaration. This was fixed before certification.
- The first UDS gate required a missing socket to remain visible as `up=0`. It now also accepts omission after reload, while the live TCP trap must remain untouched.
- The first histogram alternate exposed a false reject around an incompatible first sample. An independent compatibility preflight fixed it; both mutants still fail.
- A stock step patch passed verification but reached the 1800-second actor timeout. The final task allows 3600 seconds and its matrix was repeated.
- A method-neutral start-timestamp reader accepted coherent but non-landed formats. The final task policy was changed to upstream format conformance, so a root-only landed reader was added and the two old encodings now fail. The `st-neutral-final-*` jobs remain development history.

## Conductor rubric

The unchanged 30-criterion Conductor `task-implementation.toml` rubric has SHA-256 `8beb2c4a6faea2b5d673189b009e9a5f939eb717946372a8ace1fa475675868f`. It ran through `harbor check` with `gpt-5.6-sol`. Raw results are tracked under `.private-eval/reviews/oracle-alignment-final/`.

| Task | Raw result | Raw failures | Adjudication |
|---|---:|---|---|
| Unix-socket scraping | 28 pass / 0 fail / 2 N/A | none | clean raw result |
| Step-invariant subquery | 24 pass / 4 fail / 2 N/A | AST outcome/alignment, no-online concision, schema | AST coupling is deliberate Oracle conformance; schema rule is stale |
| Native-histogram rates | 22 pass / 6 fail / 2 N/A | no-online outcome/alignment/concision and anti-cheat, metadata wording, schema | public actor egress and the explicit no-online rule are disclosed policy limits; schema is stale |
| Start-timestamp persistence | 25 pass / 3 fail / 2 N/A | few-hours solvability, hidden conformance breadth, schema | 16-hour stretch and landed-wire policy are deliberate; schema is stale |
| Stale-series WAL expiry | 27 pass / 1 fail / 2 N/A | schema | Harbor parses and runs the valid extended schema |

The N/A criteria are structured-data schema and task README. The rubric predates valid local Harbor fields such as `network_mode` and `[[verifier.collect]]`. A stale rule is reported, not rewritten as a pass.

## Historical stock-agent calibration

These jobs used Codex 0.145.0 with `gpt-5.6-luna` and max reasoning on earlier verifier bytes. They produced eight passes under the then-current method-neutral ST gate.

| Task | Result | Wall times | Interpretation |
|---|---:|---:|---|
| Unix-socket scraping | 2/2 | 2000.9s; 1900.2s | both passed |
| Step-invariant subquery | 2/2 | 973.0s; 1491.2s | both passed |
| Native-histogram rates | 0/2 | 3245.6s; 3594.7s | both made genuine semantic misses |
| Stale-series WAL expiry | 2/2 | 1352.6s; 1154.5s | both passed |
| Start-timestamp persistence | 2/2 | 5937.57s; 5366.58s | both passed with distinct candidate encodings |

The final start-timestamp jobs had no exception or retry:

| Job | Total | Agent | Verifier | Input tokens | Cache tokens | Output tokens | Cost | Candidate archive |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `st-neutral-final-luna-r1-20260830` | 1:38:57.57 | 1:32:31.93 | 5:34.52 | 74,692,273 | 72,761,600 | 188,134 | $2.06712740 | `717ef199…` |
| `st-neutral-final-luna-r2-20260830` | 1:29:26.58 | 1:23:08.76 | 5:20.18 | 60,919,614 | 59,318,272 | 146,349 | $1.68225264 | `51336b71…` |

The candidate archives differ and use genuinely distinct encodings. Both now return reward `0` under the final landed-format reader. Trajectory review found no executed online search or fetch, verifier, solution, hidden-test, or reward access, reward hack, refusal, or timeout. R1 ran `make -n lint`, which printed a `curl` command but did not execute it.

The earlier 80% result is development history, not the final task solve rate or a Micro1 baseline/final comparison.

## Current claim

The current suite has pinned lineage, exact-reference fidelity, deterministic packaging, source parity, Harbor parsing, 5/5 reference passes, 5/5 no-op rejections, 5/5 accepted format-compatible alternates, 10/10 rejected mutants, and 2/2 rejected superseded ST encodings. The fresh 10-trial Luna-default job is still active. Repeatability on the final bytes, a formal hostile-code proof, the video, and any numerical Micro1 same-case comparison remain incomplete.
