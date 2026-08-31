# Prometheus RL environment

Prometheus already contains the range of work a coding agent should face: networking, query execution, and storage. This repository turns five merged Prometheus changes into one RL environment that runs through Harbor on Daytona.

It is built for teams training or comparing coding agents on repository-scale work. The hard part for those teams is packaging a real change into a repeatable episode without giving away the answer. Here, every task has a pinned starting tree, a short maintainer request, a captured trajectory, and a binary reward. The runtime stays the same as the work moves across the codebase.

## The five tasks

| Task | Outcome |
|---|---|
| Unix-socket scraping | Scrape HTTP and HTTPS targets over Unix sockets without mixing targets or falling back to TCP |
| Step-invariant PromQL | Keep fixed-time subqueries consistent across instant and range evaluation |
| Native-histogram rates | Handle resets, schema changes, warnings, interpolation, and mixed ranges correctly |
| Start-timestamp persistence | Preserve histogram start timestamps through chunks, WAL/WBL replay, blocks, reopen, and queries |
| Stale-series WAL expiry | Retain stale-series metadata only while WAL references still need it |

Start-timestamp persistence is the largest task. It spans 34 upstream files and is closer to a long-horizon storage change than a normal short coding episode.

## One shared episode

```text
pinned pre-change source -> coding agent -> frozen source archive
                         -> separate verifier -> reward 0 or 1
```

The agent works in a Git-stripped Prometheus tree. The upstream patch, repository history, verifier source, and hidden tests are absent. Harbor runs the episode on Daytona with 2 vCPU, 4 GiB RAM, and 10 GiB disk.

The verifier drives Prometheus behavior through live scrape targets, PromQL queries, WAL checkpoints, block reopen, replay, compaction, and iterators. Reward comes from the running system and its artifacts, never from comparing the candidate diff with the upstream diff.

That shared handoff is the practical value of the environment. A team can add or study work in another Prometheus subsystem without inventing a new actor runtime each time.

## Results

The first complete Luna cohort used max reasoning and solved 8 of 10 attempts. The final cohort used Harbor's default high reasoning and solved 2 of 10.

| Cohort | UDS | Subquery | Histogram | Start timestamp | WAL expiry | Total |
|---|---:|---:|---:|---:|---:|---:|
| First full Luna cohort, max reasoning | 2/2 | 2/2 | 0/2 | 2/2 | 2/2 | 8/10 |
| Final Luna cohort, default high reasoning | 0/2 | 0/2 | 0/2 | 0/2 | 2/2 | 2/10 |

These are milestones from the build, not a controlled model comparison. The verifier bytes and reasoning setting changed between cohorts. The [Improvement Changelog](CHANGELOG.md) records what changed and why.

All 10 final trials completed without Harbor exceptions. Together they cost `$2.59163820` and took `3:15:24.21` in summed trial time.

## Final 25-case check

The final verifier ran against five candidate states for each task:

- 5 exact upstream implementations, all accepted
- 5 unchanged implementations, all rejected
- 5 independently written working implementations, all accepted
- 10 plausible but incorrect implementations, all rejected

That is 10 correct candidates and 15 incorrect candidates. All 25 were classified correctly. On this fixed set, balanced accuracy is `1.0`, false-accept rate is `0.0`, and false-reject rate is `0.0`. Those numbers measure the verifier checks. Luna's final solve rate is the separate 2/10 result above.

## The challenging case

Start-timestamp persistence forced the clearest design decision. Two Luna solutions carried the feature through the full storage lifecycle, but each wrote its own on-disk format. Both passed an earlier behavioral verifier. Neither format matched the one Prometheus merged.

The final episode leaves implementation names and code layout open while requiring persisted blocks to work with the landed Prometheus reader. The two earlier solutions now fail that compatibility check.

Full job receipts and task digests are in the [evidence ledger](docs/TASK_SUITE_EVIDENCE.md).

## Submission map

The final submission archive keeps each part in one predictable place:

| What you need | Location |
|---|---|
| Canonical task source | `task_support/prometheus/tasks/` |
| Runnable Harbor packages | `tasks/`, created by `python3 tools/materialize_prometheus_task.py` |
| Task instructions shown to agents | `tasks/*/instruction.md` after materialization |
| Reference solutions and verifiers | `tasks/*/solution/` and `tasks/*/tests/` after materialization |
| Clean-machine commands | [`docs/REPRODUCTION.md`](docs/REPRODUCTION.md) |
| Task digests, job receipts, and run results | [`docs/TASK_SUITE_EVIDENCE.md`](docs/TASK_SUITE_EVIDENCE.md) |
| Representative agent trajectories and their reading guide | `trajectories/`, starting with `trajectories/README.md` |

The HackerEarth upload archive omits the generated `tasks/` copies to stay below its 50 MB limit. The materializer recreates them from `task_support/` and verifies their checksums.

## Reproduce it

Materialize all five task packages:

```bash
python3 tools/materialize_prometheus_task.py
python3 tools/materialize_prometheus_task.py --verify
```

The [reproduction guide](docs/REPRODUCTION.md) gives the public clone commands, pinned runtime, complete 25-case run, and Luna command. The registry is [suite.toml](task_support/prometheus/suite.toml).

## Limits

This is a transparent submission repository. It includes reference solutions and verifier code for inspection and reproduction. Before using it as a secret network-enabled evaluation set, move the hidden cases behind a private boundary.

The histogram task still has one verifier-owned Go test linked with candidate code. The other main checks run through external processes or inspect artifacts produced by candidate programs. The [verifier provenance audit](docs/VERIFIER_PROVENANCE_AUDIT.md) describes that boundary.

## License

Project-authored files use Apache-2.0. Bundled Prometheus source keeps the upstream Apache-2.0 license and notices.
