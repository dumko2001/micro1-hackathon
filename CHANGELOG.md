# Improvement Changelog

The project started with one PromQL task. These are the experiments that changed the environment.

| Stage | What we tried and why | Evidence | Decision / learning |
|---|---|---|---|
| Baseline | Packaged the clean parent of the fixed-time PromQL change with five linked semantic checks | The parent failed all five cases; the merged change passed ([build log](docs/BUILD_LOG.md#29-august-first-task)) | Keep the pinned parent, short instruction, reference patch, and binary reward as the task shape |
| Five-task environment | Added Unix-socket scraping, histogram rates, start-timestamp persistence, and stale WAL expiry to the same archive-to-verifier handoff | All five source archives and patch stacks verified against their recorded hashes ([lineage](docs/TASK_SUITE_EVIDENCE.md#registered-lineage)) | Keep one runtime while allowing each task to use a different Prometheus parent and verifier |
| Verifier separation | Removed candidate tests from reward and moved checks into controllers, readers, and sealed artifacts | UDS and PromQL run through candidate daemons; WAL and start timestamp use candidate-produced artifacts; histogram retains one linked Go test ([audit](docs/VERIFIER_PROVENANCE_AUDIT.md)) | Keep the process boundary and state the remaining histogram limitation |
| Candidate calibration | Ran references, no-ops, alternative implementations, and named defects | Calibration found a UDS false reject, a histogram compatibility error, and a constant-answer gap in the PromQL cases ([failed experiments](docs/TASK_SUITE_EVIDENCE.md#failed-experiments-kept-in-the-record)) | Accept fail-closed UDS omission, separate histogram compatibility from evaluation, and randomize PromQL controls |
| Stock-agent review | Ran two Luna-max attempts per task and inspected the submitted code | Eight of ten passed, but the two start-timestamp solutions wrote formats that Prometheus could not read; the trajectories also exposed UDS and PromQL conformance gaps ([run table](docs/TASK_SUITE_EVIDENCE.md#historical-stock-agent-calibration)) | Check reviewed Prometheus invariants where the repository or merged format defines them |
| Removed experiment | Let the start-timestamp candidate write and read any format that preserved the storage lifecycle | Two candidate-only formats passed replay, compaction, reopen, iteration, and `Seek`, then failed when read by landed Prometheus code ([conformance decision](docs/TASK_SUITE_EVIDENCE.md#start-timestamp-conformance-decision)) | Remove the candidate-only format check and require blocks that the landed reader can decode |
| Final | Ran the fixed candidate matrix and ten Luna attempts on the released task bytes | All 10 valid candidates passed and all 15 invalid candidates failed: balanced accuracy `1.0`, FAR `0.0`, FRR `0.0`. Luna passed 2/10; both passes were WAL expiry ([candidate results](docs/TASK_SUITE_EVIDENCE.md#current-daytona-results); [Luna run](docs/TASK_SUITE_EVIDENCE.md#final-byte-stock-agent-calibration)) | Freeze the five tasks, publish the evidence, and include trajectories for each agent role |

The 8/10 and 2/10 Luna results used different reasoning settings and verifier bytes. They show when design changes happened, not a controlled model comparison.

**Main failure mode:** a verifier can accept a storage format when the candidate writes and reads its own bytes. The start-timestamp task now checks those blocks with the reader built from the merged Prometheus format.

**Hot take:** keep the episode machinery fixed and change the Prometheus problem. That made failures across networking, queries, and storage comparable without forcing every task into the same verifier design.
