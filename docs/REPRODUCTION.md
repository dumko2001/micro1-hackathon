# Reproduction guide

These steps start from a clean machine, build the five task packages, run an executable baseline and reference solution, score the 25-candidate matrix, and launch the Luna evaluation.

## 1. Install the runner

Required:

- Git
- Python 3.12 or newer; recorded materialization used Python `3.14.3`
- [`uv`](https://docs.astral.sh/uv/)
- a Daytona account
- Codex model access only for the Luna run

Install the recorded Harbor version:

```bash
uv tool install harbor==0.14.0
harbor --version
```

Expected version: `0.14.0`.

The task images use Go `1.26` from the pinned builder image:

```text
golang:1.26-bookworm@sha256:e8c859f5632dcfde7b32d2012b4351728f6437930887c2f6a91ea242459e5514
```

No local Docker runtime is needed when Harbor uses Daytona.

## 2. Clone the submission

```bash
git clone https://github.com/dumko2001/micro1-hackathon.git
cd micro1-hackathon
git checkout micro1-submission-v2
```

Copy the safe environment template:

```bash
cp .env.example .env
```

Set `DAYTONA_API_KEY` in `.env`. Set `CODEX_FORCE_AUTH_JSON` to the contents of a Codex `auth.json` file only when running Luna. Do not put `.env`, provider credentials, or raw authentication files into Git or a shared result archive.

## 3. Data and task materialization

No external evaluation dataset is required. The repository contains:

- the five pre-change Prometheus source archives
- source checksums and upstream patch stacks
- task instructions
- reference solutions
- verifier code
- the calibration candidate fixtures

Materialize and verify all five Harbor packages:

```bash
python3 tools/materialize_prometheus_task.py
python3 tools/materialize_prometheus_task.py --verify
```

Expected output:

```text
verified 20 files: .../tasks/unix-socket-scraping
verified 19 files: .../tasks/prometheus-subquery-semantics
verified 20 files: .../tasks/histogram-rate-semantics
verified 22 files: .../tasks/start-timestamp-persistence
verified 21 files: .../tasks/stale-wal-expiry
```

Materialization takes under a minute on the recorded host and needs no network. The first remote run must download the pinned builder image and checksum-locked Go modules.

## 4. Executable baseline

The project story began with one fixed-time PromQL episode. For a repeatable evaluation baseline on the submitted five tasks, use Harbor's built-in no-op agent:

```bash
harbor run --env-file .env -e daytona -p tasks \
  -a nop -k 1 -n 5 \
  --cpus request --memory request \
  --override-cpus 2 --override-memory-mb 4096 --override-storage-mb 10240 \
  --delete --max-retries 1 \
  --retry-include DaytonaRateLimitError --retry-include DaytonaError \
  --yes --job-name micro1-repro-nop
```

Expected result: 5 completed trials, 5 rewards of `0`, and no exceptions. The recorded run took about 7.5 minutes with warm image caches and used no model tokens.

## 5. Reference solution

Run Harbor's built-in Oracle agent, which applies each registered reference solution:

```bash
harbor run --env-file .env -e daytona -p tasks \
  -a oracle -k 1 -n 5 \
  --cpus request --memory request \
  --override-cpus 2 --override-memory-mb 4096 --override-storage-mb 10240 \
  --delete --max-retries 1 \
  --retry-include DaytonaRateLimitError --retry-include DaytonaError \
  --yes --job-name micro1-repro-reference
```

Expected result: 5 completed trials, 5 rewards of `1`, and no exceptions. The recorded run took about 8.7 minutes with warm image caches and used no model tokens.

## 6. Final 25-candidate evaluation

The remaining 15 candidates come from the public fixture adapter in `private_eval/candidate_agent.py`. Run the working alternatives:

```bash
harbor run --env-file .env -e daytona -p tasks \
  -x unix-socket-scraping \
  --agent-import-path private_eval.candidate_agent:CandidateFixtureAgent \
  --agent-kwarg candidate_id=alternate-valid -k 1 -n 4 \
  --cpus request --memory request \
  --override-cpus 2 --override-memory-mb 4096 --override-storage-mb 10240 \
  --delete --max-retries 1 \
  --retry-include DaytonaRateLimitError --retry-include DaytonaError \
  --yes --job-name micro1-repro-alternate-main

harbor run --env-file .env -e daytona -p tasks \
  -i unix-socket-scraping \
  --agent-import-path private_eval.candidate_agent:CandidateFixtureAgent \
  --agent-kwarg candidate_id=alternate-oracle-aligned -k 1 -n 1 \
  --cpus request --memory request \
  --override-cpus 2 --override-memory-mb 4096 --override-storage-mb 10240 \
  --delete --max-retries 1 \
  --retry-include DaytonaRateLimitError --retry-include DaytonaError \
  --yes --job-name micro1-repro-alternate-uds
```

Run the two incorrect candidate sets:

```bash
harbor run --env-file .env -e daytona -p tasks \
  --agent-import-path private_eval.candidate_agent:CandidateFixtureAgent \
  --agent-kwarg candidate_id=mutant-1 -k 1 -n 5 \
  --cpus request --memory request \
  --override-cpus 2 --override-memory-mb 4096 --override-storage-mb 10240 \
  --delete --max-retries 1 \
  --retry-include DaytonaRateLimitError --retry-include DaytonaError \
  --yes --job-name micro1-repro-mutant-1

harbor run --env-file .env -e daytona -p tasks \
  --agent-import-path private_eval.candidate_agent:CandidateFixtureAgent \
  --agent-kwarg candidate_id=mutant-2 -k 1 -n 5 \
  --cpus request --memory request \
  --override-cpus 2 --override-memory-mb 4096 --override-storage-mb 10240 \
  --delete --max-retries 1 \
  --retry-include DaytonaRateLimitError --retry-include DaytonaError \
  --yes --job-name micro1-repro-mutant-2
```

Score the six jobs:

```bash
python3 tools/score_candidate_matrix.py \
  --positive jobs/micro1-repro-reference \
  --positive jobs/micro1-repro-alternate-main \
  --positive jobs/micro1-repro-alternate-uds \
  --negative jobs/micro1-repro-nop \
  --negative jobs/micro1-repro-mutant-1 \
  --negative jobs/micro1-repro-mutant-2
```

Expected result:

```json
{
  "balanced_accuracy": 1.0,
  "complete": true,
  "false_accept_rate": 0.0,
  "false_negative": 0,
  "false_positive": 0,
  "false_reject_rate": 0.0,
  "negative_cases": 15,
  "positive_cases": 10,
  "true_negative": 15,
  "true_positive": 10
}
```

The six recorded jobs took about 44 minutes when run sequentially with warm caches. They use no model tokens. Daytona infrastructure charges depend on the account plan.

## 7. Luna evaluation

Run 2 attempts per task:

```bash
harbor run --env-file .env -e daytona -p tasks \
  -a codex -m gpt-5.6-luna -k 2 -n 3 \
  --cpus request --memory request \
  --override-cpus 2 --override-memory-mb 4096 --override-storage-mb 10240 \
  --delete --max-retries 3 \
  --retry-include DaytonaRateLimitError \
  --retry-include DaytonaError \
  --retry-include ApiRateLimitError \
  --yes --job-name micro1-repro-luna
```

Expect 10 terminal trial results under `jobs/micro1-repro-luna/`. Each trial contains the instruction, Codex trajectory, timing, token and cost fields, verifier response, and binary reward.

Model results are not deterministic. The recorded final cohort returned 2/10, both on stale WAL expiry, with no scored exceptions. Its summed trial time was `3:15:24.21`, model cost was `$2.59163820`, and total output was 278,327 tokens. With three concurrent sandboxes, allow roughly 1 to 2 hours of wall time plus first-build cache time.

The earlier Luna-max cohort returned 8/10 on earlier verifier bytes. Because the reasoning setting and task checks changed, 8/10 and 2/10 are build milestones rather than a controlled accuracy comparison.

## 8. Result files

Harbor writes each job to `jobs/<job-name>/`. Keep these files for reproduction:

- job `config.json`, `lock.json`, and `result.json`
- each trial's `config.json` and `result.json`
- `agent/trajectory.json`
- verifier `reward.txt` and `status.json`
- collected candidate archive and checksum manifest

Do not publish provider credentials or raw authentication material. Representative model trajectories belong in the submission bundle; the full raw job directory can remain a reviewer artifact.
