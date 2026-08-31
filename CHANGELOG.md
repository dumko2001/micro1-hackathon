# Improvement Changelog

This project started with one PromQL task and ended with five Prometheus episodes running through the same Harbor workflow.

| Iteration | Evidence | Next decision |
|---|---|---|
| First task | The clean parent failed five fixed-time subquery cases; the merged change passed them ([build log](docs/BUILD_LOG.md)) | Keep the pre-change source, short instruction, and external reward pattern |
| Five-task environment | Prometheus had suitable networking, query, and storage changes under one Go build ([suite registry](task_support/prometheus/suite.toml)) | Add Unix sockets, histogram rates, start timestamps, and stale WAL expiry to the same episode shape |
| First Luna cohort | Luna-max passed 8/10: UDS, subquery, start timestamp, and WAL passed twice; histogram failed twice ([run table](docs/TASK_SUITE_EVIDENCE.md#historical-stock-agent-calibration)) | Inspect agent solutions and strengthen the task-specific checks before the final run |
| UDS reference stack | The first merged change let sockets sharing one authority cross streams ([build log](docs/BUILD_LOG.md)) | Include its direct pooling repair in the reference stack |
| Histogram reference stack | The first histogram change still panicked on a mixed float and histogram window ([build log](docs/BUILD_LOG.md)) | Include its direct panic repair |
| Instructions | Review found file names, commands, root causes, and routine maintainer expectations in early drafts ([final instructions](task_support/prometheus/tasks)) | Reduce every instruction to the incident and the new outcome the agent must deliver |
| Shared episode boundary | Five task-specific test scripts did not yet behave like one environment ([boundary audit](docs/VERIFIER_PROVENANCE_AUDIT.md)) | Freeze the completed repository and pass the same archive shape to a separate verifier for every task |
| Daytona runs | Remote execution exposed a loopback assumption, an out-of-memory build, and a controller error ([failed experiments](docs/TASK_SUITE_EVIDENCE.md#failed-experiments-kept-in-the-record)) | Fix the runtime assumptions, serialize Go compilation, and rerun the affected tasks |
| UDS result handling | One correct solution removed a missing target while the first check required `up=0` ([failed experiments](docs/TASK_SUITE_EVIDENCE.md#failed-experiments-kept-in-the-record)) | Accept either fail-closed representation |
| Subquery controls | One implementation could return the same fabricated answer for every query ([build log](docs/BUILD_LOG.md)) | Add independent raw and arithmetic queries with known results |
| Histogram preflight | A working solution was rejected because an incompatible first sample remained in the range ([failed experiments](docs/TASK_SUITE_EVIDENCE.md#failed-experiments-kept-in-the-record)) | Check bucket-family compatibility independently before evaluating the result |
| Start-timestamp experiment | Two Luna solutions survived replay and reopen but wrote private formats the landed Prometheus reader could not decode ([conformance decision](docs/TASK_SUITE_EVIDENCE.md#start-timestamp-conformance-decision)) | Remove the candidate-only writer/reader experiment and add an independent landed-format reader |
| Final task check | All 5 references and 5 other working implementations passed; all 5 no-ops and 10 wrong implementations failed ([Daytona results](docs/TASK_SUITE_EVIDENCE.md#current-daytona-results)) | Freeze the five task packages and record the 25 decisions |
| Final Luna cohort | Luna-high passed 2/10; both passes were stale WAL expiry ([final run table](docs/TASK_SUITE_EVIDENCE.md#final-byte-stock-agent-calibration)) | Keep the result as the final difficulty snapshot and preserve representative trajectories |

The first and final Luna cohorts used different reasoning settings, so 8/10 and 2/10 are build milestones rather than a controlled model comparison.

**Main failure mode:** start-timestamp persistence could reward storage that worked only when the candidate read its own format. The final task requires interoperability with the format Prometheus landed.

**Hot take:** Prometheus is more useful as one evolving RL environment than as a collection of isolated PR exercises. One stable episode runtime can carry an agent from networking to queries to storage.
