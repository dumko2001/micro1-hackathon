# Prometheus RL environment

Five Harbor coding episodes built from merged Prometheus work. Each episode starts from the exact pre-change source, gives a coding agent a short maintainer request, and returns a binary reward from a separate verifier.

This repository contains source lineage, task packages, exact upstream reference patches, reward logic, and calibration evidence. Harbor supplies execution and trajectory capture. It is an RL evaluation environment, not a skill, MCP server, or replacement coding agent.

## Tasks

| Harbor package | Required outcome | Reference scope |
|---|---|---|
| `unix-socket-scraping` | HTTP and HTTPS scraping over Unix sockets without cross-target pooling or TCP fallback | PR #18091 plus direct pooling correction #19399 |
| `prometheus-subquery-semantics` | Fixed-time PromQL subqueries agree across instant and range evaluation | PR #19187 |
| `histogram-rate-semantics` | Native-histogram extended ranges handle resets, schemas, warnings, and mixed windows | PR #18564 plus direct panic correction #18943 |
| `start-timestamp-persistence` | Opt-in histogram start timestamps survive chunks, WAL/WBL replay, blocks, and queries | PR #18609; later repairs excluded |
| `stale-wal-expiry` | Stale-series metadata lives exactly as long as WAL references require it | PR #18847; later fixes excluded |

The tasks share one episode shape but test different surfaces:

| Task | Candidate surface | Main verifier observation | Distinct constraint |
|---|---|---|---|
| Unix-socket scraping | scrape transport and reload | live HTTP/TLS Unix sockets and TCP fallback trap | target isolation across shared authorities |
| Step-invariant subquery | PromQL evaluation | instant and range queries over trusted data | fixed-time, nested, offset, `start()`, and `end()` cases |
| Native-histogram rates | PromQL histogram functions | API output, warnings, and one linked breadth test | schemas, resets, interpolation, and mixed windows |
| Start-timestamp persistence | chunks, WAL/WBL, blocks, and feature flags | sealed block projections read through candidate public APIs | 130-sample normal and OOO storage lifecycle |
| Stale-series WAL expiry | head compaction and checkpointing | candidate artifacts inspected by a clean-parent reader | metadata lifetime around randomized horizons |

Start-timestamp persistence is a deliberate 16-hour expert stretch. It falls outside Conductor's few-hour solvability target. The suite keeps it to test coordinated storage-format work, not as a typical episode length.

The references are exact upstream patch stacks. They are never placed in the actor filesystem, and reward never compares source diffs. Every actor archive is Git-stripped and contains no remotes, commit metadata, reference solution, or verifier source.

## Episode boundary

```text
pinned clean parent -> non-root coding agent -> frozen source archive
                    -> separate no-network verifier -> reward
```

The actor needs public egress to reach the model service. Each instruction forbids online-solution lookup, but this is a policy rule rather than a technical network control.

The verifier rejects unsafe archives and dependency drift, removes candidate tests, restores trusted harness files, and runs candidate code as UID 65532 with an empty environment, no capabilities, `no_new_privs`, and resource limits.

- Unix-socket and subquery tasks drive a real candidate Prometheus daemon from an external controller.
- WAL expiry runs a candidate program and inspects its artifacts with a trusted clean-parent reader.
- Histogram uses an external API controller plus one linked Go breadth test.
- Start timestamp builds a writer and reader from candidate source. The writer creates normal and OOO TSDB lifecycles. A root controller projects valid blocks, seals them read-only, deletes the writable database, and compares complete semantic receipts from the candidate reader. A clean-parent writer supplies legacy fixtures.

The start-timestamp verifier does not require the Oracle bitstream. That encoding was settled during review and was not derivable from the task-time contract. It grades persisted behavior through existing query and iterator APIs instead.

Histogram retains its linked-code limitation. A deliberately task-aware start-timestamp implementation could also make its writer and reader collude on a private protocol. Sealed projections, source deletion, independent legacy fixtures, and root-owned comparisons make that harder, but do not prove hostile-code resistance. See the [verifier provenance audit](docs/VERIFIER_PROVENANCE_AUDIT.md).

## Frozen evidence

The registered alternate and mutant results below were collected immediately before the final senior-maintainer prompt rewrite. The current prompt bytes have fresh two-run reference and no-op controls for every task. The step verifier was then strengthened with randomized exact-output controls and separately repeated at reference `2/2` and no-op `2/2`.

| Gate | Result |
|---|---:|
| Deterministic materialization and source integrity | 5/5 |
| Exact reference, 2 Daytona runs per task | 10/10 reward `1` |
| No-op, 2 Daytona runs per task | 10/10 reward `0` |
| Alternate-valid fixtures | 5/5 accepted |
| Named behavioral mutants | 15/15 rejected |
| Private full calibration gate | 30/30 decisions; BA `1.0`, FAR `0.0`, FRR `0.0` |
| Private repeatability gate | 20/20 decisions; BA `1.0`, FAR `0.0`, FRR `0.0` |

Start timestamp now has seven rejected mutants covering flag coupling, OOO downgrade, recode loss, always-on persistence, block loss, stale recovery, and `Seek`. Its alternate passed the method-neutral verifier. These results establish repeatability and discrimination for the registered candidates, not universal correctness.

Final task digests and job-level evidence are in the [evidence ledger](docs/TASK_SUITE_EVIDENCE.md).

## Build and verify

Materialization is local and deterministic:

```bash
python3 tools/materialize_prometheus_task.py
python3 tools/materialize_prometheus_task.py --verify
```

The [reproduction guide](docs/REPRODUCTION.md) covers public source checks and Harbor/Daytona runs. Its reviewer-only section explains the private evidence bundle. The registry is [suite.toml](task_support/prometheus/suite.toml).

## Micro1 status

The project documents the move from an initial PromQL episode to five calibrated Prometheus environments. The [changelog](CHANGELOG.md) records each verifier correction, false reject, runtime failure, and hardening decision made along the way.

On the current prompt bytes, ten `gpt-5.6-luna` rollouts with no reasoning override produced seven raw verifier passes: UDS, step, and WAL returned two passes; start timestamp returned one; histogram returned none. Harbor's Codex adapter used its default `high` setting, not `max`. All ten trials finished without infrastructure exceptions. Step R1 preceded the final exact-output verifier hardening, so only its instruction and source—not its verifier bytes—match the final package. These runs measure task difficulty; they do not by themselves prove every reward decision correct.

The solution video, redacted representative trajectories, and a shareable commit remain submission work. See the [Micro1 checklist](docs/MICRO1_REQUIREMENTS.md).

## Publishing

This checkout has no commit or Git remote. It is not public.

The authoring tree contains solutions and verifier cases. It can be published as a transparent submission and reproduction artifact, but not as a secret network-enabled benchmark. A live secret benchmark needs unreleased cases, private evaluator storage, and runtime-only credentials. The [publishing guide](docs/PUBLISHING.md) keeps those release modes separate.

## License

Project-authored files use Apache-2.0. Bundled Prometheus source keeps the upstream Apache-2.0 license and notices. Complete the dependency and image notice review before publishing a release archive.
