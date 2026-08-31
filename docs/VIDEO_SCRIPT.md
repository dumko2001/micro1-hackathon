# Micro1 video script

Recording cut. Read at a natural pace; target length is about 4 minutes 40 seconds.

## 0:00-0:35 - Problem and starting point

“Coding-agent environments can look valid while grading the wrong thing. At the start of this project, I had one Prometheus task for fixed-time PromQL subqueries and a narrow, reference-shaped verifier. It could distinguish the clean parent from the merged fix on five assertions, but it had no alternate-valid corpus, behavioral mutants, cloud evidence binding, or strong actor-verifier boundary.

The user is a coding-agent or RL team that needs realistic software-engineering episodes with rewards they can trust.”

On screen: the first task, its short instruction, and the opening row of the changelog.

## 0:35-1:15 - What I built

“I turned that starting point into a Harbor RL environment around Prometheus. It contains five coding episodes: Unix-socket scraping, fixed-time PromQL subqueries, native-histogram rate semantics, histogram start-timestamp persistence, and stale-series WAL expiry.

Each episode starts from the exact source immediately before the upstream change. The agent receives a short maintainer request, not the patch, target files, root cause, or hidden tests. Harbor runs the agent on Daytona, freezes its Git-stripped source tree, and passes that archive to a separate no-network verifier.”

On screen: the five-task table and the actor-to-verifier diagram from the README.

## 1:15-2:10 - What the verifier checks

“The exact merged PR, or the exact two-PR stack when a direct follow-up repaired the first change, is the positive Oracle. I used the Oracle and its review history to identify the load-bearing engineering concerns, then checked their consequences without requiring private helper names or source layout.

Unix-socket cases cover HTTP, HTTPS, Host and TLS identity, reloads, normal TCP behavior, pool reuse, cross-target isolation, and fail-closed missing sockets. PromQL cases cover real instant and range results, the reviewed preprocessing boundary, histogram resets, interpolation, schemas, warnings, and mixed samples. Storage cases cover WAL and WBL replay, compaction, block reopen, stale recovery, recoding, feature flags, legacy reads, and iterator Seek.

Start timestamp is deliberately an upstream-conformance task. Candidate code may use different Go names and organization, but its persistent blocks must interoperate with a root-only reader built from the final reviewed patch.”

On screen: one public positive behavior and one named mutant category. Do not show hidden fixtures.

## 2:10-2:50 - One execution

“Here is one complete run. Harbor started stale-series WAL expiry in Daytona with two CPUs, four gigabytes of memory, and ten gigabytes of disk. Luna inspected the Git-stripped source, changed the expiry from the WAL-segment domain to the timestamp domain, and ran focused checks. Harbor collected a checksummed source archive and started the separate verifier.

The verifier created real checkpoints, inspected them with clean-parent code, and checked the exact retention boundary. This run returned reward one in 15 minutes 42.28 seconds, with no Harbor exception.”

On screen: condensed trajectory `stale-wal-expiry__V8VwEHg`, then its reward receipt. Hide credentials and raw hidden-test output.

## 2:50-3:35 - Final evidence

“I did not stop when the Oracle passed. On the final task bytes, all five references returned one, all five no-op candidates returned zero, five registered Oracle-compatible alternates returned one, and ten plausible mutants returned zero. Two formerly accepted non-landed start-timestamp encodings also returned zero.

The bound 25-case gate reports balanced accuracy 1.0, false-accept rate zero, and false-reject rate zero. I also ran two completed Luna attempts per task with default high reasoning. WAL passed twice; the other four tasks passed zero of two. The final solve rate is two out of ten, with no infrastructure exceptions and a total model cost of 2 dollars and 59 cents.”

On screen: the 25-case gate followed by the final 2/10 task table.

## 3:35-4:15 - Baseline, final state, and challenging case

“The changelog is the baseline comparison I can support. The project moved from one narrow task and five parent-versus-reference assertions to five process-separated tasks and 25 evidence-bound candidate decisions. I did not run the old and new verifiers over one identical candidate corpus, so I do not claim a numerical accuracy delta or invent baseline runtime and cost.

The hardest case was start-timestamp persistence. A method-neutral verifier accepted two coherent solutions with incompatible on-disk formats. That revealed a real product decision: this episode should measure compatibility with Prometheus’s reviewed persistent format. I added the independent landed reader, kept names and source organization free, and replayed the old solutions. Both correctly failed.”

On screen: the relevant start-timestamp changelog rows and the before/after verifier boundary.

## 4:15-4:45 - Takeaway

“The biggest improvement was treating the verifier as part of the product. Alternate-valid implementations exposed false rejects. Mutants exposed false accepts. Separate processes reduced reward-hacking surfaces. Repeated Daytona runs exposed runtime and resource defects that static review missed.

My hot take is that a benchmark is not trustworthy because its reference patch passes. It becomes trustworthy when valid alternatives pass, realistic wrong fixes fail, the evidence is bound to exact bytes, and the remaining limitations are stated plainly.”

On screen: the final evidence table, then the repository title.
