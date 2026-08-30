# Micro1 video script

Draft only. Do not record the final version until every bracketed baseline/final value is replaced with measured evidence from the same frozen cases.

## 0:00-0:35 - Problem and baseline

"Coding-agent environments can look valid while grading the wrong thing. A simple PR-derived baseline is easy to make: take the repository before a merged change, give an agent the issue, and run a few upstream tests. But that baseline can accept partial fixes, reject equally valid implementations, or leak the reference implementation through internal names and test structure.

Our user is a coding-agent or RL team that needs realistic software-engineering episodes with rewards they can trust."

On screen: one clean-parent task package, its short instruction, and the simple baseline verifier.

## 0:35-1:15 - What we built

"We built a Harbor RL environment around Prometheus. We selected five post-May 2026 engineering changes and converted them into five coding episodes: Unix-socket scraping, fixed-time PromQL subqueries, native-histogram rate semantics, histogram start-timestamp persistence, and stale-series WAL expiry. Three episodes use one merged PR; Unix sockets and histogram rates use an exact two-PR stack because a direct follow-up corrected the original change.

Each episode starts from the exact pre-change Prometheus source. The agent receives a short maintainer request, not the patch, target files, root cause, or hidden tests. Harbor runs the agent in Daytona, freezes its source tree, and sends that tree to a separate no-network verifier."

On screen: the five-task table from `README.md`, followed by the actor-to-verifier diagram.

## 1:15-2:10 - Oracle fidelity and behavioral verification

"The exact merged PR, or exact corrected PR stack where a direct follow-up was required, is our positive Oracle. We used the Oracle and its review history to identify every load-bearing engineering concern, then tested the observable consequence rather than copying private helper names or source structure.

For Unix sockets, positive cases cover HTTP, HTTPS, Host and TLS identity, reloads, ordinary TCP, and two sockets sharing one advertised address. Negative cases reject connection-pool crossover and any TCP fallback from a missing socket.

For PromQL, we compare real instant and range API results across fixed-time, nested, offset, reset, schema, warning, and mixed-sample cases. For storage, we exercise real WAL and WBL restart, compaction, block reopen, stale recovery, recoding, feature flags, legacy reads, and iterator Seek behavior."

On screen: one positive case and one negative case from the selected demo task.

## 2:10-3:05 - One execution from start to finish

"Here is one realistic execution. Harbor starts the pinned task in Daytona with two CPUs, four gigabytes of memory, and ten gigabytes of disk. The coding agent inspects the Git-stripped Prometheus source, reproduces the symptom, changes the implementation, and runs its own focused checks. Harbor then stops the actor, collects a checksummed source archive, and starts the separate verifier.

The verifier launches the candidate Prometheus behavior, drives the hidden positive and negative cases, and returns a binary reward. This current-prompt run received reward [CURRENT DEMO REWARD] in [CURRENT DEMO WALL TIME], with no Harbor exception."

On screen: condensed trajectory from instruction to patch to verifier receipt. Do not expose hidden fixtures or credentials.

## 3:05-3:55 - Calibration evidence

"We did not stop when the Oracle passed. On the final prompt-matched task bytes, the exact references passed [ORACLE RESULT], no-op candidates were rejected [NO-OP RESULT], independently structured valid implementations were accepted [ALTERNATE RESULT], and plausible behavioral mutants were rejected [MUTANT RESULT]. The registered candidate gate reports [BALANCED ACCURACY], with [FALSE ACCEPT RATE] false accepts and [FALSE REJECT RATE] false rejects.

We also ran two independent Luna-max coding agents on every task. [CURRENT STOCK RESULT]."

On screen: the frozen calibration table and the 8/10 stock-agent table.

## 3:55-4:30 - Required Micro1 comparison

"For the same [NUMBER] frozen candidate cases, the simple baseline verifier scored [BASELINE PRIMARY METRIC], while the final workflow scored [FINAL PRIMARY METRIC], a change of [CHANGE]. Baseline runtime and cost were [BASELINE RUNTIME AND COST]; final runtime and cost were [FINAL RUNTIME AND COST]. The challenging case was [CASE], which revealed [LEARNING]."

On screen: the complete baseline-versus-final table. Do not substitute Oracle/no-op smoke results for this comparison.

## 4:30-5:00 - Changelog and hot take

"The biggest improvement was treating the verifier as part of the product. Alternate-valid implementations exposed false rejects; mutants exposed false accepts; and the separate process boundary reduced reward hacking.

One experiment we removed was exact-byte decoding for the start-timestamp format. Review history showed that those bytes were not specified at task time, and two coherent implementations were rejected for solving the behavior differently. We kept the exact PR as the positive Oracle, but moved reward to persistent behavior.

My hot take is that a benchmark is not trustworthy because the reference patch passes. It becomes trustworthy only when valid alternatives pass, realistic wrong fixes fail, and those decisions repeat on frozen infrastructure."
