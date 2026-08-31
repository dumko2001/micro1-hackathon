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
| Start-timestamp persistence | chunks, WAL/WBL, blocks, and feature flags | sealed blocks read by candidate and landed-format readers | lifecycle correctness plus wire-format compatibility |
| Stale-series WAL expiry | head compaction and checkpointing | candidate artifacts inspected by a clean-parent reader | metadata lifetime around randomized horizons |

Start-timestamp persistence is a deliberate 16-hour expert stretch. It falls outside the copied Conductor rubric's few-hour solvability criterion. The suite keeps it to test coordinated storage-format work, not as a typical episode length.

The references are exact upstream patch stacks. They are never placed in the actor filesystem, and reward never compares source diffs. Every actor archive is Git-stripped and contains no remotes, commit metadata, reference solution, or verifier source.

## Episode boundary

```text
pinned clean parent -> non-root coding agent -> frozen source archive
                    -> separate no-network verifier -> reward
```

The actor needs public egress to reach the model service. Each instruction forbids online-solution lookup, but this is a policy rule rather than a technical network control.

The verifier rejects unsafe archives and dependency drift, removes candidate tests, restores trusted harness files, and runs candidate code as UID 65532 with an empty environment, no capabilities, `no_new_privs`, and resource limits.

- Unix-socket and subquery tasks drive a real candidate Prometheus daemon from an external controller. UDS also checks effective pool identity through the pre-existing scrape-pool seam; subquery also checks the reviewed preprocessing invariant through the exported AST.
- WAL expiry runs a candidate program and inspects its artifacts with a trusted clean-parent reader.
- Histogram uses an external API controller plus one linked Go breadth test.
- Start timestamp builds a writer and reader from candidate source. The writer creates normal and OOO TSDB lifecycles. A root controller projects valid blocks, seals them read-only, deletes the writable database, and compares complete semantic receipts from the candidate reader. A clean-parent writer supplies legacy fixtures. A second root-only reader built from the landed patch must decode the same blocks.

The start-timestamp task is intentionally an upstream-conformance episode. It does not require the landed Go type names or source layout, but it does require blocks to use the final reviewed wire format. Two previously accepted Luna-max solutions used coherent alternative encodings; both now return reward `0` when replayed against the landed reader.

Histogram retains its linked-code limitation. A deliberately task-aware start-timestamp implementation could also make its writer and reader collude on a private protocol. Sealed projections, source deletion, independent legacy fixtures, and root-owned comparisons make that harder, but do not prove hostile-code resistance. See the [verifier provenance audit](docs/VERIFIER_PROVENANCE_AUDIT.md).

## Frozen evidence

The latest Oracle-alignment pass uses one final-byte reference, no-op, alternate, and 2-mutant decision per task. Start timestamp was then rebound separately after the landed-format reader was added. Every run used Harbor on Daytona at 2 vCPU, 4096 MiB RAM, and 10240 MiB disk.

| Gate | Result |
|---|---:|
| Deterministic materialization and source integrity | 5/5 |
| Exact reference on current verifier bytes | 5/5 reward `1` |
| No-op on current verifier bytes | 5/5 reward `0` |
| Alternate-valid fixtures | 5/5 accepted |
| Current named behavioral mutants | 10/10 rejected |
| Replayed non-landed ST encodings | 2/2 rejected |
| Bound 25-case private gate | BA `1.0`, FAR `0.0`, FRR `0.0` |

Earlier frozen snapshots also contain repeat runs and a broader 15-mutant corpus. They remain useful development evidence, but their task digests differ from the final Oracle-conformance package and are not presented as current-byte certification.

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

Ten final-byte `gpt-5.6-luna` rollouts are complete: 2 per task with no reasoning override, which Harbor resolved to its default `high` setting. WAL passed 2/2; UDS, subquery, histogram, and start timestamp passed 0/2. The aggregate is 2/10 with no Harbor exceptions, $2.59163820 in model cost, and 3:15:24.21 of summed trial wall time. Earlier cohorts remain development history, including the two ST solutions that passed the method-neutral verifier but fail the final landed-format gate. Agent solve rate measures difficulty; it does not establish verifier validity.

The recording script is ready. The actual video, redacted representative trajectories, and a shareable remote remain submission work. See the [Micro1 checklist](docs/MICRO1_REQUIREMENTS.md).

## Publishing

This checkout has a local Git commit but no GitHub remote yet. It is not public.

The authoring tree contains solutions and verifier cases. It can be published as a transparent submission and reproduction artifact, but not as a secret network-enabled benchmark. A live secret benchmark needs unreleased cases, private evaluator storage, and runtime-only credentials. The [publishing guide](docs/PUBLISHING.md) keeps those release modes separate.

## License

Project-authored files use Apache-2.0. Bundled Prometheus source keeps the upstream Apache-2.0 license and notices. Complete the dependency and image notice review before publishing a release archive.
