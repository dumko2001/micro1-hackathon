# Prometheus RL environment

This project turns five merged Prometheus changes into coding episodes for reinforcement learning and agent evaluation. Each episode starts from the source just before the change, gives the agent a short maintainer request, and returns a binary reward from a separate verifier.

It is for teams that want repository-scale work rather than isolated coding puzzles. Their bottleneck is packaging a real change so the starting state, runtime, trajectory, and reward are repeatable without revealing the answer. Once that episode boundary is shared, the same team can train or compare agents across networking, query, and storage work without rebuilding the infrastructure for every task.

## The five tasks

| Task | What the agent has to achieve |
|---|---|
| Unix-socket scraping | Scrape HTTP and HTTPS targets over Unix sockets without mixing targets or falling back to TCP |
| Step-invariant PromQL | Keep fixed-time subqueries consistent across instant and range evaluation |
| Native-histogram rates | Handle resets, schema changes, warnings, interpolation, and mixed ranges correctly |
| Start-timestamp persistence | Preserve histogram start timestamps through chunks, WAL/WBL replay, blocks, reopen, and queries |
| Stale-series WAL expiry | Retain stale-series metadata only while WAL references still need it |

The start-timestamp task is the largest. It spans 34 upstream files and is closer to a long-horizon storage change than a normal short coding episode.

## One episode

```text
pinned pre-change source -> coding agent -> frozen source archive
                         -> separate verifier -> reward 0 or 1
```

The agent receives a Git-stripped Prometheus tree. It does not receive the upstream patch, repository history, verifier source, or hidden tests. Harbor runs the episode on Daytona with 2 vCPU, 4 GiB RAM, and 10 GiB disk.

The verifier exercises the candidate through Prometheus behavior: live scrape targets, PromQL queries, WAL checkpoints, block reopen, replay, compaction, and iterators. It does not compare the candidate diff with the upstream diff.

## What changed while building it

The first complete Luna cohort solved 8 of 10 attempts at max reasoning. After the task contracts and verifiers were brought in line with the final Prometheus behavior, the final cohort solved 2 of 10 attempts at Harbor's default high reasoning.

| Cohort | UDS | Subquery | Histogram | Start timestamp | WAL expiry | Total |
|---|---:|---:|---:|---:|---:|---:|
| First full Luna cohort, max reasoning | 2/2 | 2/2 | 0/2 | 2/2 | 2/2 | 8/10 |
| Final Luna cohort, default high reasoning | 0/2 | 0/2 | 0/2 | 0/2 | 2/2 | 2/10 |

This is the build history, not a controlled model comparison: the verifier bytes and reasoning setting changed between the two cohorts. The [Improvement Changelog](CHANGELOG.md) connects each iteration to the evidence that led to the next decision.

All 10 final trials completed without Harbor exceptions. Together they cost `$2.59163820` and took `3:15:24.21` in summed trial time.

## Final checks

The final verifier was run against 25 labeled candidates across the five tasks:

- 5 exact upstream implementations, all accepted
- 5 unchanged implementations, all rejected
- 5 independently written working implementations, all accepted
- 10 plausible but incorrect implementations, all rejected

That gives 10 correct candidates and 15 incorrect candidates. All 25 were classified correctly, so balanced accuracy is `1.0`, false-accept rate is `0.0`, and false-reject rate is `0.0` on this fixed set. These numbers describe the verifier checks; the separate 2/10 result above describes Luna's solve rate.

The hardest case was start-timestamp persistence. Two Luna solutions preserved the feature through the full storage lifecycle but wrote a different on-disk format. They passed an earlier behavioral verifier and failed once the task required compatibility with the format Prometheus actually merged. That result changed the final task boundary: implementation names and code layout remain free, but persisted blocks must be readable by the landed Prometheus reader.

Full job receipts and task digests are listed in the [evidence ledger](docs/TASK_SUITE_EVIDENCE.md).

## Reproduce it

Materialize all five task packages:

```bash
python3 tools/materialize_prometheus_task.py
python3 tools/materialize_prometheus_task.py --verify
```

The [reproduction guide](docs/REPRODUCTION.md) contains the pinned runtime, public clone commands, and Harbor/Daytona run shape. The task registry is [suite.toml](task_support/prometheus/suite.toml).

## Limits

This public repository includes the reference solutions and verifier code so the submission can be inspected and reproduced. It should not be used as a secret, network-enabled evaluation set without moving hidden cases behind a private boundary.

The histogram task still uses one verifier-owned Go test linked with candidate code. The other main checks run through external processes or inspect artifacts produced by candidate programs. Details are in the [verifier provenance audit](docs/VERIFIER_PROVENANCE_AUDIT.md).

## License

Project-authored files use Apache-2.0. Bundled Prometheus source keeps the upstream Apache-2.0 license and notices.
