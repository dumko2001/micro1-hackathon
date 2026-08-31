# Reproduction guide

This guide reproduces task materialization and the Harbor/Daytona runs used for the five Prometheus episodes.

## Clean checkout

Clone the public submission and check out its release tag:

```bash
git clone https://github.com/dumko2001/micro1-hackathon.git
cd micro1-hackathon
git checkout micro1-submission-v1
```

The repository includes the task code, reference patches, and verifier internals. Provider credentials, raw job directories, recordings, and unredacted trajectories are not part of Git.

## Pinned runtime

- Harbor `0.14.0`
- Python `3.14.3` for recorded materialization
- Go `1.26`
- builder `golang:1.26-bookworm@sha256:e8c859f5632dcfde7b32d2012b4351728f6437930887c2f6a91ea242459e5514`
- registry `task_support/prometheus/suite.toml`
- Conductor rubric SHA-256 `8beb2c4a6faea2b5d673189b009e9a5f939eb717946372a8ace1fa475675868f`

Materialization needs no network. Image construction needs the pinned builder and checksum-locked Go modules. The verifier runs separately with `network_mode=no-network`. A model actor needs public egress to reach its provider.

## Materialize and verify

```bash
python3 tools/materialize_prometheus_task.py
python3 tools/materialize_prometheus_task.py --verify
```

Expected file counts are:

```text
unix-socket-scraping          20
prometheus-subquery-semantics 19
histogram-rate-semantics      20
start-timestamp-persistence   22
stale-wal-expiry              21
```

Verify source archives independently:

```bash
for source in task_support/prometheus/tasks/*/source; do
  (cd "$source" && sha256sum -c SOURCE.SHA256SUMS)
done
```

Expected result: five `OK` lines. Also require Harbor to parse all five generated task directories before remote execution.

## Host parent/reference check

For each task:

1. Extract its registered clean-parent archive twice.
2. Apply the registered upstream patch stack to one copy.
3. Remove candidate or reference-added tests.
4. Restore the clean-parent test harness.
5. Add the verifier-owned cases to both copies.
6. Run the same focused Go command.
7. Require parent failure and reference success.

Start-timestamp persistence uses external programs rather than reference-owned tests linked with candidate code. A writer and reader built from candidate source exercise real storage and the pre-existing query and iterator surface. The root controller projects blocks into a read-only tree, deletes the writable database, and compares complete receipts. A clean-parent writer creates legacy fixtures. A second root-only reader built from the exact landed patch must decode the candidate blocks and return the same receipts. The candidate cannot read that source or binary.

## Daytona matrix

Keep the Daytona token in gitignored `.env`. The frozen jobs use 2 vCPU, 4096 MiB RAM, 10240 MiB disk, and at most five concurrent sandboxes. No local Docker runtime is part of the recorded evidence.

The common Harbor shape is:

```bash
harbor run --env-file .env -e daytona \
  -p tasks -a <agent> -k 1 -n 5 \
  --cpus request --memory request \
  --override-cpus 2 --override-memory-mb 4096 --override-storage-mb 10240 \
  --delete --max-retries 1 \
  --retry-include DaytonaRateLimitError --retry-include DaytonaError \
  --yes --job-name <job-name>
```

The current deterministic matrix uses these jobs:

```text
micro1-oracle-alignment-final-oracle-20260830
micro1-oracle-alignment-final-nop-20260830
micro1-oracle-alignment-final-alternate-main-20260830
micro1-oracle-alignment-final-alternate-uds-20260830
micro1-oracle-alignment-final-mutant-1-20260830
micro1-oracle-alignment-final-mutant-2-20260830
st-oracle-conformance-final-oracle-20260830
st-oracle-conformance-final-nop-20260830
st-oracle-conformance-final-alternate-20260830
st-oracle-conformance-final-mutant-1-20260830
st-oracle-conformance-final-mutant-2-20260830
```

Oracle and no-op use Harbor's built-in agents. Alternate and mutant runs use the reviewer-only candidate-fixture adapter. The current matrix expects five Oracle `1`s, five no-op `0`s, five alternate `1`s, and ten mutant `0`s, with no Harbor exceptions. Earlier repeat jobs and the seven-mutant ST corpus are retained as development evidence on superseded task digests.

The final stock-agent calibration is composed from the eight terminal trials in `micro1-oracle-alignment-final-luna-default-20260830` plus the terminal replacement jobs `micro1-oracle-alignment-final-recovery-uds-20260831` and `micro1-oracle-alignment-final-recovery-20260831`. Require exactly two completed trials per task, two total rewards of `1`, eight rewards of `0`, and zero exceptions. The replaced coordinator entries have no reward and are not part of the scored corpus.

## Author-side evidence gates

This transparent authoring repository includes `.private-eval`, candidate fixtures, manifests, and rubric results. It excludes raw jobs and credentials. The following historical commands reproduce the two bound gates on their pinned earlier task bytes:

```bash
python3 .private-eval/grade.py \
  --manifest .private-eval/cases/manifest.json \
  jobs/micro1-prometheus-oracle-r1-v2-20260830 \
  jobs/micro1-prometheus-nop-r1-20260830 \
  jobs/micro1-prometheus-alternate-valid-final-20260830 \
  jobs/micro1-prometheus-mutant-1-20260830 \
  jobs/micro1-prometheus-mutant-2-20260830 \
  jobs/uds-contract-final-oracle-r1-20260830 \
  jobs/uds-contract-final-nop-r1-20260830 \
  jobs/uds-contract-final-alternate-valid-20260830 \
  jobs/uds-contract-final-mutant-1-20260830 \
  jobs/uds-contract-final-mutant-2-20260830 \
  jobs/step-timeout-20260830-oracle-r1 \
  jobs/step-timeout-20260830-nop-r1 \
  jobs/step-timeout-20260830-alternate-valid \
  jobs/step-timeout-20260830-mutant-1 \
  jobs/step-timeout-20260830-mutant-2 \
  jobs/hist-finaldoc-20260830-oracle-r1 \
  jobs/hist-finaldoc-20260830-nop-r1 \
  jobs/hist-finaldoc-20260830-alternate-valid \
  jobs/hist-finaldoc-20260830-mutant-1 \
  jobs/hist-finaldoc-20260830-mutant-2 \
  jobs/st-neutral-final-oracle-r1-20260830 \
  jobs/st-neutral-final-nop-r1-20260830 \
  jobs/st-neutral-final-alternate-valid-20260830 \
  jobs/st-neutral-final-mutant-1-20260830 \
  jobs/st-neutral-final-mutant-2-20260830 \
  jobs/st-neutral-final-mutant-3-20260830 \
  jobs/st-neutral-final-mutant-4-20260830 \
  jobs/st-neutral-final-mutant-5-20260830 \
  jobs/st-neutral-final-mutant-6-20260830 \
  jobs/st-neutral-final-mutant-7-20260830

python3 .private-eval/grade.py \
  --manifest .private-eval/cases/repeatability-manifest.json \
  jobs/micro1-prometheus-oracle-r1-v2-20260830 \
  jobs/micro1-prometheus-oracle-r2-20260830 \
  jobs/micro1-prometheus-nop-r1-20260830 \
  jobs/micro1-prometheus-nop-r2-20260830 \
  jobs/uds-contract-final-oracle-r1-20260830 \
  jobs/uds-contract-final-oracle-r2-20260830 \
  jobs/uds-contract-final-nop-r1-20260830 \
  jobs/uds-contract-final-nop-r2-20260830 \
  jobs/step-timeout-20260830-oracle-r1 \
  jobs/step-timeout-20260830-oracle-r2 \
  jobs/step-timeout-20260830-nop-r1 \
  jobs/step-timeout-20260830-nop-r2 \
  jobs/hist-finaldoc-20260830-oracle-r1 \
  jobs/hist-finaldoc-20260830-oracle-r2 \
  jobs/hist-finaldoc-20260830-nop-r1 \
  jobs/hist-finaldoc-20260830-nop-r2 \
  jobs/st-neutral-final-oracle-r1-20260830 \
  jobs/st-neutral-final-oracle-r2-20260830 \
  jobs/st-neutral-final-nop-r1-20260830 \
  jobs/st-neutral-final-nop-r2-20260830
```

Expected result for both gates: `complete: true`, balanced accuracy `1.0`, false-accept rate `0.0`, and false-reject rate `0.0`.

The current 25-case Oracle-conformance matrix is recorded directly in the evidence ledger. The older manifests must not be relabeled as current-byte certification.

## Build-time context

The first PromQL snapshot took 142.91 seconds for a cold focused test, 215.33 seconds for the first broad Prometheus build after that, and 23.08 seconds for an immediate warm rebuild on the author's macOS host. These are host observations, not Daytona timings. The evidence ledger records whole-job Daytona times.

## Recorded build milestones

The first complete Luna cohort used 2 max-reasoning attempts per task and passed 8/10. The final cohort used 2 attempts per task with Harbor's default high reasoning and passed 2/10. The verifier version and reasoning setting changed, so these are build milestones rather than a controlled model comparison.

The separate 25-case task check classified all 10 working candidates and all 15 incorrect candidates correctly. It measures the final verifier on its registered candidates; it is not an agent solve-rate result.
