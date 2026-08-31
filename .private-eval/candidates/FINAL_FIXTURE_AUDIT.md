# Final calibration-fixture audit

Date: 2026-08-30

This file records the fixture audit at that stage. The start-timestamp verifier was subsequently changed from lifecycle method neutrality to explicit conformance with the final reviewed wire format. Current certification is recorded in `cases/oracle-conformance-manifest.json` and `docs/TASK_SUITE_EVIDENCE.md`.

## Verdict

All 20 registered alternate and mutant fixtures apply cleanly to fresh copies of the current clean-parent archives. Every alternate passes its available discriminator and every mutant fails for its intended behavior. The five source archives in `task_support` are byte-identical to the corresponding generated task archives.

One limitation remains: the start-timestamp alternate is Oracle-dependent and changes only chunk-encoding dispatch. It proves that the verifier is not source-diff grading, but it is not an independent implementation of the new codecs or persistence pipeline. Treat that as a P1 calibration gap if an independent alternate implementation is required.

## Matrix

| Task | Fixture | Construction | Static apply | Host discriminator | Quality verdict |
|---|---|---|---|---|---|
| Unix socket | alternate | Clean parent; owned per-target Unix transports | Pass | Pass | Independent organization |
| Unix socket | mutant 1 | First feature patch only | Pass | Fail: Unix/Unix, Unix/TCP, and reload isolation | partial-feature mutant |
| Unix socket | mutant 2 | Oracle plus TCP fallback | Pass | Fail: missing socket reached TCP | fail-closed mutant |
| Step invariant | alternate | Clean parent; generic wrapper guard | Pass | Pass | Independent control point |
| Step invariant | mutant 1 | Oracle plus start/end wrapping | Pass | Fail: `@ start()` and `@ end()` | optimizer mutant |
| Step invariant | mutant 2 | Oracle plus offset wrapping | Pass | Fail: fixed subquery with offset | optimizer mutant |
| Histogram rate | alternate | Clean parent; normalized window plus existing `histogramRate` | Pass | Pass | Independent computation model |
| Histogram rate | mutant 1 | Feature patch without panic correction | Pass | Fail: mixed-type smoothed selector panic | partial-feature mutant |
| Histogram rate | mutant 2 | Oracle with reset-blind interpolation | Pass | Fail: double, shared-boundary, right-boundary, and short-window resets | numerical mutant |
| Start timestamp | alternate | Oracle plus table-backed chunk dispatch | Pass | Pass | Valid but weak independence; Oracle-dependent |
| Start timestamp | mutant 1 | Oracle with coupled feature flags | Pass | Fail: XOR2-only independence control | configuration mutant |
| Start timestamp | mutant 2 | Oracle with legacy OOO histogram encodings | Pass | Fail: integer and float OOO encoding cases | persistence mutant |
| Start timestamp | mutant 3 | Oracle with corrupted integer-histogram layout recode | Pass | Fail: 130-sample receipt | recode mutant |
| Start timestamp | mutant 4 | Oracle with always-on histogram ST encoding | Pass | Fail: disabled-mode lifecycle | feature-gate mutant |
| Start timestamp | mutant 5 | Oracle with durable block-reader ST loss | Pass | Fail: custom-profile block receipt | persistence mutant |
| Start timestamp | mutant 6 | Oracle with stale-to-live ST loss | Pass | Fail: stale recovery lifecycle | recovery mutant |
| Start timestamp | mutant 7 | Oracle with iterator Seek off by one | Pass | Fail: exact-timestamp Seek receipt | iterator mutant |
| WAL expiry | alternate | Clean parent; pre-existing `updateWALExpiry` helper | Pass | Pass | Independent existing-convention path |
| WAL expiry | mutant 1 | Clean parent with `maxt-1` | Pass | Fail: inclusive boundary and stored expiry | boundary mutant |
| WAL expiry | mutant 2 | Clean parent with unbounded expiry | Pass | Fail: exact expiry and later checkpoint removal | retention mutant |

## Evidence scope

- Static checks used a fresh extraction for every fixture and applied each prerequisite Oracle patch in the same order as its `solve.sh`.
- Current verifier controllers for all five tasks compile on the host. The corrected start-timestamp candidate program and Oracle reader also compile.
- Unix-socket, step-invariant, and histogram host semantics used the prior in-process hidden suites because their current process-level controllers require Harbor's separate verifier, launcher, UID, and root-only assets. Those focused suites exercise the same named behaviors, but they are not substitutes for a current Harbor result.
- This table began as a host-fixture audit. Final Daytona evidence is bound separately: the start-timestamp Oracle passed twice, its no-op failed twice, its registered alternate passed, and all seven named mutants failed without exceptions.

## Rejected fixture found during audit

The previous start-timestamp mutant 2 forced a legacy option only in WBL subset reconstruction. It passed the focused TSDB suite and a direct OOO candidate/trusted-reader replay, so it was not a discriminator. It was replaced with a defect in OOO histogram chunk encoding. The replacement fails `TestOOOChunks_ToEncodedChunks_WithST` for both integer and float histograms while applying cleanly after the Oracle.
