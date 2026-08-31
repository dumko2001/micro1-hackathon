# Improvement changelog

This experiment log records the move from one narrow task to five frozen Harbor episodes with repeated runtime calibration. It is not Git history.

- **Starting point:** one fixed-time PromQL episode with a narrow reference-shaped verifier.
- **Current state:** five Git-stripped, PR-derived Prometheus episodes with separate verifiers, repeated reference/no-op controls, accepted alternate implementations, rejected behavioral mutants, and stock-agent calibration on Daytona.

| Stage | Change | Evidence and decision |
|---|---|---|
| First episode | Built the fixed-time PromQL task from an exact clean parent | The parent failed five assertions; the exact PR passed. Kept the episode model. |
| Source lineage | Added four Prometheus tasks, each with its own parent, archive hash, and exact patch stack | All five archives verify and every stack applies in order. |
| Prompt rewrite | Reduced instructions to the incident and genuinely new public contract | No target files, commands, root causes, patch structure, Oracle reasoning, or checklist of routine senior-maintainer obligations is disclosed. |
| Senior-maintainer prompt pass | Removed explicit reminders about regression safety, fail-closed behavior, lifecycle completeness, and backward compatibility | Those expectations remain in the verifier because they follow from established Prometheus behavior. Rematerialization and Harbor parsing pass; runtime evidence must be rebound to the new instruction bytes. |
| Git stripping | Removed repository history and provenance metadata from actor archives | Actor source has no `.git`, remote, solution, hidden test, or commit variable. |
| UDS correction | Rejected PR #18091 alone after same-authority sockets crossed streams | The reference is now #18091 plus direct pooling repair #19399. |
| UDS false reject | A missing socket disappeared after reload instead of remaining visible as `up=0` | Accepted omission or `up=0` as fail-closed, while keeping the TCP fallback trap mandatory. Repeated the matrix. |
| Histogram correction | Rejected PR #18564 alone after a mixed float/histogram window still panicked | Added only its direct correction #18943. |
| Scope correction | Reclassified #18609 from a small WAL repair to a 34-file storage feature | Gave it a long-horizon budget and excluded later repairs. |
| Trusted harness | Removed candidate tests and restored clean-parent harnesses before adding verifier-owned cases | Clean parents fail and exact references pass the focused behavior. |
| Process isolation | Moved UDS and subquery checks to external controllers; added external artifact inspection for WAL and start timestamp | Candidate code no longer shares the controller process for these observable gates. Histogram retains one linked breadth test. |
| Runtime hardening | Ran candidate programs as UID 65532 with an empty environment, no capabilities, `no_new_privs`, and resource limits | Fixed-token and candidate-helper bypasses no longer issue reward. This is hardening, not a hostile-code proof. |
| Remote diagnostics | Exercised the verifier on Daytona at 2 vCPU, 4 GiB RAM, and 10 GiB disk | Removed a false loopback assumption, serialized Go compilation after an OOM, and fixed a controller declaration error. |
| Histogram false reject | The first alternate failed because an incompatible first sample remained in the range | Added an independent bucket-family preflight. The corrected alternate passes while reset and interpolation mutants fail. |
| Step timeout | A stock agent produced a passing patch but reached the 1800-second actor limit | Raised only the actor budget to 3600 seconds and repeated the current-byte reference, no-op, alternate, and mutant runs. |
| Numeric tolerance | Review found the histogram controller's `1e-12` relative comparator undocumented | Documented its floating-point purpose and mutant calibration, then repeated the candidate matrix. |
| Step exact-output control | A fresh Harbor review showed that equality plus non-emptiness could accept a server returning one fabricated result for every query | Randomized the metric identities, added independently known raw and arithmetic matrices, and required task-query output to differ from the controls. The exact reference passed twice and no-op failed twice on the strengthened verifier. |
| Start-timestamp collection | Go builds could leave `go.work.sum` in the actor tree | Removed the build byproduct before collection and repeated the matrix. |
| Start-timestamp method experiment | An exact-format reader rejected coherent implementations that used another on-disk encoding | Temporarily moved reward to candidate writer/reader lifecycle behavior. This exposed what agents could solve without wire-format conformance. |
| Start-timestamp Oracle decision | Chose the final reviewed PR format as part of the upstream-conformance task | Restored a root-only landed-format reader. It checks sealed blocks without requiring the Oracle's Go names or source organization. Both formerly passing alternative encodings now return `0`. |
| Repeatability | Repeated exact-reference and no-op runs on frozen bytes | 10/10 reference decisions returned `1`; 10/10 no-op decisions returned `0`; no exceptions or retries. |
| Method check | Ran one registered alternate-valid fixture per task | 5/5 accepted. The ST alternate reorganizes dispatch but keeps the landed persistent format. |
| Mutant check | Ran 15 named plausible defects | 15/15 rejected. Start timestamp contributes seven storage, flag, recovery, and iterator defects. |
| Evidence binding | Bound Harbor job, task, candidate, verifier, reward, and artifact bytes in a private grader | The 30-case full gate and 20-case repeat gate both report BA `1.0`, FAR `0.0`, and FRR `0.0`. |
| Oracle-alignment review | Replayed trajectory-derived alternatives against reviewed PR invariants | UDS now checks pool identity and reuse; PromQL checks the reviewed AST invariant; histogram and WAL retain behavioral conformance; ST checks landed wire compatibility. |
| Final deterministic matrix | Repeated the current Oracle, no-op, alternate, and 2-mutant cases on Daytona | References 5/5, no-ops 0/5, alternates 5/5, mutants 0/10; all trials ended without Harbor exceptions. |
| Final evidence binding | Bound the 25 current decisions to native Harbor metadata, candidate bytes, verifier receipts, and task checksums | The current Oracle-conformance gate reports BA `1.0`, FAR `0.0`, and FRR `0.0`. |
| Stock-agent calibration | Ran 2 fixed `gpt-5.6-luna` max-reasoning rollouts per task | UDS, step, WAL, and ST passed 2/2; histogram produced 2 genuine semantic misses. Suite result: 8/10, or 80%. |
| Pre-final prompt-matched calibration | Ran 2 current-instruction `gpt-5.6-luna` rollouts per task with no reasoning override | Harbor used its default `high` setting. UDS, step, and WAL returned 2/2; start timestamp returned 1/2; histogram returned 0/2. Step R1 preceded the final exact-output verifier hardening, so this is development history rather than final-byte evidence. |
| Final-byte agent calibration | Ran 2 completed `gpt-5.6-luna` rollouts per final task with no reasoning override | WAL returned 2/2; UDS, step, histogram, and start timestamp returned 0/2. Suite result: 2/10, no Harbor exceptions, $2.59163820, and 3:15:24.21 summed trial wall time. Two trials stranded by a stopped local coordinator were replaced and excluded rather than treated as failures. |

The primary verifier metric is balanced accuracy on independently labeled candidates, with false-accept and false-reject rates reported separately. Agent solve rate measures difficulty; it does not establish verifier validity.

The main lesson is that the task boundary needed as much testing as the feature. Valid alternatives, plausible wrong methods, repeated cloud runs, and the actor/verifier split each found a different problem.
