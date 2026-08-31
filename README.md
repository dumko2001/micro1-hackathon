# Prometheus RL environment

Prometheus changes span networking, query execution, and storage. This repository turns five merged changes into one RL environment that runs through Harbor on Daytona.

Teams training or comparing coding agents need to package a repository change as a repeatable episode without giving away the answer. Each task here has a pinned starting tree, a short maintainer request, a captured trajectory, and a binary reward. The runtime stays the same as the work moves across the codebase.

The seven upstream PRs were merged between 18 May and 14 August 2026. Choosing recent changes reduces the chance of training exposure; it does not prove that a model has never seen the code.

## The five tasks

| Task | Upstream PRs | Outcome |
|---|---|---|
| Unix-socket scraping | [#18091](https://github.com/prometheus/prometheus/pull/18091), [#19399](https://github.com/prometheus/prometheus/pull/19399) | Scrape HTTP and HTTPS targets over Unix sockets without mixing targets or falling back to TCP |
| Step-invariant PromQL | [#19187](https://github.com/prometheus/prometheus/pull/19187) | Keep fixed-time subqueries consistent across instant and range evaluation |
| Native-histogram rates | [#18564](https://github.com/prometheus/prometheus/pull/18564), [#18943](https://github.com/prometheus/prometheus/pull/18943) | Handle resets, schema changes, warnings, interpolation, and mixed ranges correctly |
| Start-timestamp persistence | [#18609](https://github.com/prometheus/prometheus/pull/18609) | Preserve histogram start timestamps through chunks, WAL/WBL replay, blocks, reopen, and queries |
| Stale-series WAL expiry | [#18847](https://github.com/prometheus/prometheus/pull/18847) | Retain stale-series metadata only while WAL references still need it |

Start-timestamp persistence spans 34 upstream files, more than the other four tasks.

## One shared episode

```text
pinned pre-change source -> coding agent -> frozen source archive
                         -> separate verifier -> reward 0 or 1
```

The agent works in a Git-stripped Prometheus tree. The upstream patch, repository history, verifier source, and hidden tests are absent. Harbor runs the episode on Daytona with 2 vCPU, 4 GiB RAM, and 10 GiB disk.

The verifier drives Prometheus behavior through live scrape targets, PromQL queries, WAL checkpoints, block reopen, replay, compaction, and iterators. Reward comes from the running system and its artifacts, never from comparing the candidate diff with the upstream diff.

The same handoff works across all five tasks. A team can add another Prometheus subsystem without writing a new actor runtime.

## Results

Each complete cohort used two Luna attempts per task, for ten attempts in total. The first complete cohort used max reasoning and solved 8 of 10. The final cohort used Harbor's default high reasoning and solved 2 of 10.

| Cohort | UDS | Subquery | Histogram | Start timestamp | WAL expiry | Total |
|---|---:|---:|---:|---:|---:|---:|
| First full Luna cohort, max reasoning | 2/2 | 2/2 | 0/2 | 2/2 | 2/2 | 8/10 |
| Final Luna cohort, default high reasoning | 0/2 | 0/2 | 0/2 | 0/2 | 2/2 | 2/10 |

These are milestones from the build, not a controlled model comparison. The verifier bytes and reasoning setting changed between cohorts. The [Improvement Changelog](CHANGELOG.md) records what changed and why.

All 10 final trials completed without Harbor exceptions. Together they cost `$2.59163820` and took `3:15:24.21` in summed trial time.

## Final 25-case check

The final checker made five decisions for each task:

- the merged implementation should pass
- unchanged code should fail
- a different working implementation should pass
- two intentionally wrong implementations should fail

Across five tasks, that is 10 working candidates and 15 incorrect candidates. All 25 were classified correctly. On this fixed set, balanced accuracy is `1.0`, false-accept rate is `0.0`, and false-reject rate is `0.0`. Those numbers measure the checker. Luna's final solve rate is the separate 2/10 result above.

## The challenging case

Start-timestamp persistence exposed a verifier gap. Two Luna solutions carried the feature through the storage lifecycle, but each wrote its own on-disk format. Both passed an earlier behavioral verifier. Neither format matched the one Prometheus merged.

The final episode leaves implementation names and code layout open while requiring persisted blocks to work with the merged Prometheus reader. The two earlier solutions now fail that compatibility check.

Job receipts and task digests are in the [evidence ledger](docs/TASK_SUITE_EVIDENCE.md).

## Submission map

The submission archive uses these paths:

| What you need | Location |
|---|---|
| Canonical task source | `task_support/prometheus/tasks/` |
| Runnable Harbor packages | `tasks/`, created by `python3 tools/materialize_prometheus_task.py` |
| Task instructions shown to agents | `tasks/*/instruction.md` after materialization |
| Reference solutions and verifiers | `tasks/*/solution/` and `tasks/*/tests/` after materialization |
| Clean-machine commands | [`docs/REPRODUCTION.md`](docs/REPRODUCTION.md) |
| Task digests, job receipts, and run results | [`docs/TASK_SUITE_EVIDENCE.md`](docs/TASK_SUITE_EVIDENCE.md) |
| Completed Luna trajectories and their index | `trajectories/`, starting with `trajectories/README.md` |

The HackerEarth upload archive omits the generated `tasks/` copies to stay below its 50 MB limit. The materializer recreates them from `task_support/` and verifies their checksums.

A trajectory records the instruction, agent messages, tool calls, tool responses, and outcome. A raw Harbor job also contains working directories, checker output, collected repository archives, runtime logs, and coordinator state.

The upload contains 42 completed, exception-free Luna trajectories. Its index also accounts for five excluded trial slots: two cancellations, one actor timeout, one UDS run stranded before grading, and one start-timestamp slot that stopped before writing a trajectory. Raw jobs stay local.

## Reproduce it

Materialize all five task packages:

```bash
python3 tools/materialize_prometheus_task.py
python3 tools/materialize_prometheus_task.py --verify
```

The [reproduction guide](docs/REPRODUCTION.md) gives the public clone commands, pinned runtime, 25-case run, and Luna command. The registry is [suite.toml](task_support/prometheus/suite.toml).

## Limits

This repository includes reference solutions and verifier code for inspection and reproduction. Before using it as a secret network-enabled evaluation set, move the hidden cases behind a private boundary.

The histogram task still has one verifier-owned Go test linked with candidate code. The other checks run through external processes or inspect artifacts produced by candidate programs. The [verifier provenance audit](docs/VERIFIER_PROVENANCE_AUDIT.md) describes that boundary.

## License

Project-authored files use Apache-2.0. Bundled Prometheus source keeps the upstream Apache-2.0 license and notices.
