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

## Current and calibrated Harbor task digests

| Task | Current prompt-tightened SHA-256 | Previously calibrated SHA-256 | Files |
|---|---|---|---:|
| Unix-socket scraping | `05d8ad20bca1a6d219230f99857adb0f5aabad6c78b5965f7304a33890aed408` | `3a986ebb2e926b9314a0359db5e3b46d45c7955ca1dc5585511fd771033c0739` | 19 |
| Step-invariant subquery | `9bba37a998f7f0155536f7fa019f5c584ac5f656970040856d00170524c19c96` | `ba05dcfef28c72fddfe64c3b77449e88d72fc34ae6a66b51c3722d9cb32a4756` | 18 |
| Native-histogram rates | `f350fbb854d6fb0f9163c77b2834a9477e92b25059c5da2c7ea94d2a459d557e` | `884f463e0d4bd9c5e253d84045f24b66970aa632f165f2432788049454f76f36` | 20 |
| Start-timestamp persistence | `7bcfab6d49fd9b4d988aee464c717e878f875395a7f37ddaa9776a60bcebb184` | `faba462bbfb4c3c614d8b8778d5e5ee74104f0395af42312e98183f79dbfb057` | 21 |
| Stale-series WAL expiry | `ed115231760f7ec36a695616ad891c8b171977e4bc67513e3fa8a684d353e18c` | `8ce6a3a21fcc1f92774602fa09670aab1ab8c3ea4374ca3a7838348314fb9487` | 21 |

Only the instruction bytes changed. Verify mode, Harbor parsing, source parity, and no-`.git` checks pass on the current packages. The Daytona jobs below bind to the previously calibrated digests and must be repeated before they are claimed for the current prompt-tightened packages.

## Task shape and verifier boundary

| Task | Shared episode shape | Unique verifier observation | Remaining limitation |
|---|---|---|---|
| Unix-socket scraping | clean parent, non-root actor, separate verifier | live randomized HTTP/TLS sockets, Host/SNI, reload, target isolation, TCP control and fallback trap | actor egress makes the no-search rule a policy control |
| Step-invariant subquery | same | instant, range, nested, numeric, `start()`, `end()`, offset, and ordinary queries over trusted data | focused cases do not cover all PromQL behavior |
| Native-histogram rates | same | daemon/API output, warnings, resets, schemas, panic resistance, and linked interpolation breadth | candidate code shares a process for the linked breadth test |
| Start-timestamp persistence | same | candidate reader observes root-owned sealed blocks; controller compares complete receipts; clean-parent writer supplies legacy fixtures | a deliberate writer/reader protocol could collude |
| Stale-series WAL expiry | same | clean-parent reader checks candidate checkpoints and replay across randomized horizons | pre-existing internal retention conventions are intentionally enforced |

Candidate programs run as UID 65532 with an empty environment, `no_new_privs`, no capabilities, and resource limits. Build sources are removed before executable gates run. These controls reduce the tested attack surface. They do not prove safety against arbitrary hostile code.

## Repeated Daytona results

Harbor used Daytona only. Every sandbox requested 2 vCPU, 4096 MiB RAM, and 10240 MiB disk, with at most five concurrent sandboxes.

The jobs in this section bind to the previously calibrated digests in the table above. They predate the instruction-only senior-maintainer prompt rewrite and are not current-byte certification.

| Task | Reference r1/r2 | No-op r1/r2 | Alternate | Named mutants | Exceptions |
|---|---|---|---|---:|---:|
| Unix-socket scraping | `uds-contract-final-oracle-r1-20260830` / `uds-contract-final-oracle-r2-20260830` | `uds-contract-final-nop-r1-20260830` / `uds-contract-final-nop-r2-20260830` | `uds-contract-final-alternate-valid-20260830` | 2 | 0 |
| Step-invariant subquery | `step-timeout-20260830-oracle-r1` / `step-timeout-20260830-oracle-r2` | `step-timeout-20260830-nop-r1` / `step-timeout-20260830-nop-r2` | `step-timeout-20260830-alternate-valid` | 2 | 0 |
| Native-histogram rates | `hist-finaldoc-20260830-oracle-r1` / `hist-finaldoc-20260830-oracle-r2` | `hist-finaldoc-20260830-nop-r1` / `hist-finaldoc-20260830-nop-r2` | `hist-finaldoc-20260830-alternate-valid` | 2 | 0 |
| Start-timestamp persistence | `st-neutral-final-oracle-r1-20260830` / `st-neutral-final-oracle-r2-20260830` | `st-neutral-final-nop-r1-20260830` / `st-neutral-final-nop-r2-20260830` | `st-neutral-final-alternate-valid-20260830` | 7 | 0 |
| Stale-series WAL expiry | `micro1-prometheus-oracle-r1-v2-20260830` / `micro1-prometheus-oracle-r2-20260830` | `micro1-prometheus-nop-r1-20260830` / `micro1-prometheus-nop-r2-20260830` | `micro1-prometheus-alternate-valid-final-20260830` | 2 | 0 |

All ten reference decisions and five alternates returned `1`. All ten no-op decisions and 15 mutants returned `0`. The repeated pairs establish repeatability for the pinned runs, not a probabilistic reliability bound.

Reference r1 wall times, including Daytona setup and verifier lifecycle, were 382.7s for UDS, 361.8s for step, 358.8s for histogram, 563.9s for start timestamp, and 203.9s for WAL.

## Alternate-valid and mutant calibration

The UDS alternate constructs a transport per target. Step uses a different wrapper guard. Histogram normalizes the window and checks bucket families independently. WAL factors expiry through another helper path. The start-timestamp alternate passes without a verifier-owned exact decoder.

| Task | Mutant 1 | Mutant 2 | Additional start-timestamp mutants |
|---|---|---|---|
| Unix-socket scraping | cross-target pooling | TCP fallback | — |
| Step-invariant subquery | wrong wrapping boundary | `start()`/`end()`-only fix | — |
| Native-histogram rates | partial mixed-window/panic fix | reset interpolation defect | — |
| Start-timestamp persistence | feature flags coupled | OOO encoding downgrade | recode loss; always-on persistence; block loss/read repair; stale-recovery defect; `Seek` defect |
| Stale-series WAL expiry | off-by-one lifetime | retain forever | — |

The start-timestamp corpus has 130 samples. It crosses recode and chunk thresholds, expands compatible bucket layouts, changes zero thresholds, recovers from stale markers, reopens WAL/WBL and normal/OOO blocks, and exercises fresh and past-end `Seek`. The root controller compares timestamp, start timestamp, kind, reset state, schema, zero threshold and count, bucket populations, custom bounds, count, sum, ordering, and cardinality. Equivalent span segmentation is accepted.

## Start-timestamp false-reject correction

The first external design used a trusted reader for the final Oracle bitstream. Two clean stock implementations chose different coherent encodings and were rejected before their behavior could be judged.

That requirement was unfair. The public proposal did not specify the bitstream, the PR author's first version used another header, and the final layout emerged during review. The exact decoder and Oracle patch were removed from the verifier image.

The final gate builds both writer and reader from candidate source. The candidate writer creates real normal and OOO lifecycles. A root controller projects valid blocks into a new location, makes them root-owned and read-only, deletes the original writable database, and seals the parent. The candidate reader then uses the pre-existing public querier and iterator APIs against that projection. A clean-parent writer independently creates legacy integer and float fixtures. The root controller computes expected receipts and performs every comparison.

This accepts alternate encodings while checking the required persistence behavior. A deliberately coordinated writer and reader could still invent a private protocol, so method neutrality is demonstrated for the registered alternate rather than proved for hostile code.

## Private evidence gates

The private grader binds task digest, candidate identity, agent, resource request, artifact hash, verifier status, reward, and job ID. It rejects missing or extra cases, path escapes, links, mismatched rewards, and infrastructure states.

| Gate | Decisions | Complete | Balanced accuracy | False accepts | False rejects |
|---|---:|---:|---:|---:|---:|
| Full: reference, no-op, alternate, and mutants | 30 | yes | `1.0` | `0.0` | `0.0` |
| Repeatability: reference r1/r2 and no-op r1/r2 | 20 | yes | `1.0` | `0.0` | `0.0` |

These metrics apply only to the registered candidates and pinned jobs. The manifests, fixtures, reports, and raw jobs are reviewer-only and gitignored. Give judges the private bundle through restricted access or an encrypted archive, and record its SHA-256 in the release manifest.

## Failed experiments kept in the record

- An early diagnostic treated every non-loopback interface as a network-policy failure. Daytona still exposes an interface in the verifier sandbox. The final gate relies on the backend network policy and tests application behavior.
- Parallel Go compilation exceeded the 4 GiB limit. Final builds use `GOMAXPROCS=2`, `CGO_ENABLED=0`, `-p=1`, and serialized compilation.
- A generated start-timestamp controller referenced its database handle before declaration. This was fixed before certification.
- The first UDS gate required a missing socket to remain visible as `up=0`. It now also accepts omission after reload, while the live TCP trap must remain untouched.
- The first histogram alternate exposed a false reject around an incompatible first sample. An independent compatibility preflight fixed it; both mutants still fail.
- A stock step patch passed verification but reached the 1800-second actor timeout. The final task allows 3600 seconds and its matrix was repeated.
- An exact start-timestamp decoder rejected alternative on-disk layouts. It was removed for the task-time fairness reasons above. The `st-neutral-final-*` jobs certify the previously calibrated verifier design, not the later prompt-only package digest.

## Conductor rubric

The unchanged 30-criterion Conductor `task-implementation.toml` rubric has SHA-256 `8beb2c4a6faea2b5d673189b009e9a5f939eb717946372a8ace1fa475675868f`. It ran through `harbor check` with `gpt-5.6-sol`. Raw results remain in the gitignored reviewer directory.

| Task | Raw result | Raw failures | Adjudication |
|---|---:|---|---|
| Unix-socket scraping | 27 pass / 1 fail / 2 N/A | `task_toml_schema` | stale rubric schema; Harbor parses and runs the task |
| Step-invariant subquery | 25 pass / 3 fail / 2 N/A | schema plus `verifiable` and separate-verifier cascades | all three arise from the stale schema rule; runtime evidence confirms collection and separate verification |
| Native-histogram rates | 25 pass / 3 fail / 2 N/A | schema plus the same 2 cascades | same stale-rule cascade; no additional task defect identified |
| Start-timestamp persistence | 26 pass / 2 fail / 2 N/A | `solvable`; `task_toml_schema` | `solvable` is a genuine failure because the expert estimate is 16 hours; schema is stale |
| Stale-series WAL expiry | 28 pass / 0 fail / 2 N/A | none | no raw failure |

The N/A criteria are structured-data schema and task README. The rubric predates valid local Harbor fields such as `network_mode` and `[[verifier.collect]]`. A stale rule is reported, not rewritten as a pass.

## Stock-agent calibration

All jobs use Codex 0.145.0 with `gpt-5.6-luna` and max reasoning. The ten runs produced eight verifier passes, a stock solve rate of 80%.

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

The candidate archives differ and use genuinely distinct encodings. Trajectory review found no executed online search or fetch, verifier, solution, hidden-test, or reward access, reward hack, refusal, or timeout. R1 ran `make -n lint`, which printed a `curl` command but did not execute it.

The old exact-decoder ST diagnostics are false-reject evidence, not model failures, and are excluded from solve rate. The 80% result measures stock difficulty only. It is not a Micro1 baseline/final comparison.

## Current claim

The current prompt-tightened suite has pinned lineage, exact-reference fidelity, deterministic packaging, source parity, and Harbor parsing. Its immediately preceding digests have repeated reference/no-op discrimination, five accepted alternates, 15 rejected mutants, and an 8/10 stock calibration. Fresh runtime binding is required before those results can be promoted to the current task bytes. A formal hostile-code proof and the Micro1 same-case baseline/final comparison are also incomplete.
