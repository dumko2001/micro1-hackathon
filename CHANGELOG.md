# Changelog

This project started with one PromQL task and ended with five runnable Prometheus episodes.

| Stage | What changed | What we learned |
|---|---|---|
| First task | Built fixed-time PromQL subqueries from the source immediately before the upstream change | The clean parent failed five focused cases and the merged change passed them. The task shape worked. |
| Five-task environment | Added Unix-socket scraping, native-histogram rates, start-timestamp persistence, and stale-series WAL expiry | Each task needed its own source archive, patch stack, instruction, and verifier. |
| First Luna run | Ran 2 Luna-max attempts per task | UDS, subquery, start timestamp, and WAL passed twice. Histogram failed twice. Total: 8/10. |
| UDS correction | Added the direct follow-up fix to the reference stack | The first merged change allowed sockets sharing one authority to cross streams. |
| Histogram correction | Added the direct follow-up fix to the reference stack | The original change still panicked on a mixed float and histogram window. |
| Instruction pass | Removed target files, commands, root causes, and reminders a Prometheus maintainer should infer from the repository | The final instructions describe outcomes and new contracts without walking the agent through the patch. |
| Separate verification | Moved checking out of the agent process and ran the tasks through Harbor on Daytona | Remote runs exposed a loopback assumption, an out-of-memory build, and a controller error. |
| UDS result handling | Accepted either target removal or an `up=0` result when a socket disappears | Both outcomes fail closed; requiring only one representation rejected sound work. |
| Subquery correction | Added independent raw and arithmetic queries | The first equality check could be satisfied by returning one fabricated result for every query. |
| Histogram correction | Added an independent bucket-family preflight | The first working alternative was rejected because an incompatible first sample remained in the range. |
| Start-timestamp experiment | Temporarily accepted any format that survived a candidate writer and reader | Two Luna solutions passed while writing private formats that Prometheus could not read. |
| Start-timestamp decision | Added an independent reader built from the landed Prometheus patch | Candidate code can be organized differently, but persisted blocks must remain compatible with Prometheus. The 2 earlier solutions now fail. |
| Final task matrix | Ran the reference, no-op, another working implementation, and 2 plausible wrong implementations for every task | All 25 decisions were correct: balanced accuracy 1.0, false-accept rate 0.0, and false-reject rate 0.0. |
| Final Luna run | Ran 2 fresh attempts per task with Harbor's default high reasoning | WAL passed twice. The other 8 attempts failed. Total: 2/10. |

The first and final Luna cohorts used different reasoning settings, so the change from 8/10 to 2/10 is a build milestone rather than a controlled model comparison.

The main failure was in start-timestamp persistence: a solution could preserve the feature while writing storage that only its own reader understood. The final task keeps implementation choices open but requires compatibility with Prometheus's landed format.
