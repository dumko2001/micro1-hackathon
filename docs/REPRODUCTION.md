# Reproduction guide

From a clean machine, the sequence is: clone the repository, materialize the five tasks, run the no-op and reference controls, score the 25 candidates, then launch Luna. The commands below match the recorded Harbor/Daytona setup.

## 1. Prepare the runner

Required:

- Git
- Python 3.12 or newer; recorded materialization used Python `3.14.3`
- [`uv`](https://docs.astral.sh/uv/)
- a Daytona account
- Codex model access only for the Luna run

Install the Harbor version used for the recorded runs:

```bash
uv tool install harbor==0.14.0
harbor --version
```

The command should report `0.14.0`.

The task images use Go `1.26` from the pinned builder image:

```text
golang:1.26-bookworm@sha256:e8c859f5632dcfde7b32d2012b4351728f6437930887c2f6a91ea242459e5514
```

Harbor delegates execution to Daytona, so this path does not need local Docker.

## 2. Clone the environment

```bash
git clone https://github.com/dumko2001/micro1-hackathon.git
cd micro1-hackathon
git checkout micro1-submission-v3
```

Create the local environment file from the safe template:

```bash
cp .env.example .env
```

Add `DAYTONA_API_KEY` to `.env`. The Luna run also needs `CODEX_FORCE_AUTH_JSON` set to the compact, single-line JSON from a Codex `auth.json` file; pretty-printed multiline JSON is not a valid dotenv value. Keep `.env`, provider credentials, and raw authentication files out of Git and shared result archives.

## 3. Materialize the tasks

There is no separate evaluation download. The repository already contains:

- the five pre-change Prometheus source archives
- source checksums and upstream patch stacks
- task instructions
- reference solutions
- verifier code
- the calibration candidate fixtures

Build and verify the five Harbor packages:

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

On the recorded host, materialization took under a minute and used no network. The first Daytona run still has to fetch the pinned builder image and checksum-locked Go modules.

## 4. Run the executable baseline

The project began with one fixed-time PromQL episode. To get a repeatable baseline across the submitted five tasks, run Harbor's built-in no-op agent:

```bash
harbor run --env-file .env -e daytona -p tasks \
  -a nop -k 1 -n 5 \
  --cpus request --memory request \
  --override-cpus 2 --override-memory-mb 4096 --override-storage-mb 10240 \
  --delete --max-retries 1 \
  --retry-include DaytonaRateLimitError --retry-include DaytonaError \
  --yes --job-name micro1-repro-nop
```

Expect 5 completed trials, 5 rewards of `0`, and no exceptions. With warm image caches, the recorded run took about 7.5 minutes and used no model tokens.

## 5. Run the reference solutions

Harbor's built-in Oracle agent applies the registered reference solution for each task:

```bash
harbor run --env-file .env -e daytona -p tasks \
  -a oracle -k 1 -n 5 \
  --cpus request --memory request \
  --override-cpus 2 --override-memory-mb 4096 --override-storage-mb 10240 \
  --delete --max-retries 1 \
  --retry-include DaytonaRateLimitError --retry-include DaytonaError \
  --yes --job-name micro1-repro-reference
```

Expect 5 completed trials, 5 rewards of `1`, and no exceptions. With warm image caches, the recorded run took about 8.7 minutes and used no model tokens.

## 6. Score the 25 candidates

The no-op and reference jobs cover 10 candidates. The other 15 come from the public fixture adapter at `private_eval/candidate_agent.py`. First run the working alternatives:

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

Then run the two incorrect candidate sets:

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

Score all six jobs together:

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

Run sequentially with warm caches, the six recorded jobs took about 44 minutes. They use no model tokens. Daytona infrastructure charges depend on the account plan.

## 7. Run Luna

Launch 2 attempts for each task:

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

The run should create 10 terminal trial results under `jobs/micro1-repro-luna/`. Each one contains the instruction, Codex trajectory, timing, token and cost fields, verifier response, and binary reward.

Model results vary from run to run. The recorded final cohort returned 2/10, both on stale WAL expiry, with no scored exceptions. Its summed trial time was `3:15:24.21`, model cost was `$2.59163820`, and total output was 278,327 tokens. With three concurrent sandboxes, allow roughly 1 to 2 hours of wall time plus the first-build cache time.

An earlier Luna-max cohort returned 8/10 on earlier verifier bytes. The reasoning setting and task checks changed before the final run, so 8/10 and 2/10 are build milestones rather than a controlled accuracy comparison.

## 8. Keep the result files

Harbor writes every job to `jobs/<job-name>/`. Retain these files:

- job `config.json`, `lock.json`, and `result.json`
- each trial's `config.json` and `result.json`
- `agent/trajectory.json`
- verifier `reward.txt` and `status.json`
- collected candidate archive and checksum manifest

Keep provider credentials and raw authentication material private. Put representative model trajectories in the submission bundle. The complete raw job directory can stay as a reviewer artifact.
