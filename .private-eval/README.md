# Private evidence gates

This tracked directory contains author-side release criteria and calibration
fixtures. It is not actor input, and an empty manifest is not evidence of a
result. Raw Harbor jobs and credentials remain ignored.

## Two evidence gates

- `cases/oracle-conformance-manifest.json` binds the 25 decisions on the final
  Oracle-conformance packages: reference, no-op, registered compatible
  alternate, and two named mutants per task. It is the current-byte gate.

- `cases/runtime-smoke-manifest.json` covers only the five Daytona oracle runs
  and five Daytona no-op runs. Passing it proves bound `1/0` smoke behavior; it
  does **not** prove alternate-valid method neutrality, mutant discrimination,
  repeated-run stability, or stock-agent difficulty.
- `cases/manifest.json` is the full 30-case calibration gate. It additionally
  requires clean-parent, registered alternate-valid, and named behavioral-mutant
  trials. Four alternates use meaningfully different implementation strategies;
  the start-timestamp alternate remains Oracle-dependent and does not prove full
  codec method neutrality. Start timestamp has seven named mutants covering
  flag coupling, OOO downgrade, recode corruption, always-on encoding, block
  reads, stale-to-live recovery, and iterator seek; the bound corpus is complete.
- `cases/repeatability-manifest.json` binds two Oracle and two no-op runs for
  every task. Job names are part of case identity, so repeated trials cannot be
  silently exchanged.

All manifests require Harbor 0.14, Daytona, at most five concurrent trials,
exactly 2 vCPU / 4096 MiB / 10240 MiB overrides, and sandbox deletion.

When a five-task Harbor job contains trials from task bytes later superseded by
a focused repair, `ignored_evidence` names the exact job/task pair and reason.
The grader requires each rule to match once; unrelated or silently extra trials
still fail the gate.

## Harbor-native evidence flow

`grade.py` takes completed Harbor job directories directly:

```sh
python3 .private-eval/grade.py --emit-bindings \
  jobs/oracle-one jobs/oracle-two jobs/nop-one jobs/nop-two
```

The smoke invocation must include all ten job directories (or fewer job
directories containing exactly those ten completed trials). `--emit-bindings`
validates the evidence and prints a candidate `evidence_bindings` object. It
never edits a manifest and always reports `complete: false`. Review that output,
copy the bindings into the private manifest, freeze the job directories, and run
the same command without `--emit-bindings`:

```sh
python3 .private-eval/grade.py \
  jobs/oracle-one jobs/oracle-two jobs/nop-one jobs/nop-two
```

For an author-controlled freeze, `--pin-bindings` performs the same validation
and atomically writes the complete binding set. It refuses partial or failing
evidence. A second run without either flag is still required for certification.

Use `--manifest .private-eval/cases/manifest.json` only for the full calibration
corpus. Full-calibration cases whose agent names are not unique must be pinned by
reviewed job and trial IDs; an ambiguous unpinned corpus is intentionally
rejected.

## What is bound and checked

The grader reads native job `config.json`, `lock.json`, and `result.json`; native
trial `config.json` and `result.json`; `artifacts/manifest.json`; and the collected
`candidate.tar.gz` / `candidate.sha256`. It cross-links job and trial UUIDs,
names, URI, embedded config, task identity, lock entry, agent, aggregate reward,
terminal counts, exceptions, Daytona resources, and artifact mappings.

Every accepted case pins hashes for all job/trial metadata files, the artifact
manifest, the raw candidate archive, and a canonical candidate-tree digest. The
tree digest ignores tar order, owners, timestamps, and gzip headers while keeping
paths, executable bits, sizes, and bytes significant. Archive traversal, links,
special entries, duplicate paths, symlinked evidence, oversized expansion, and
unrequested artifacts fail closed. Infrastructure exceptions never count as a
behavioral reward of zero.

## Harbor quality check rubrics

`rubrics/conductor-task-implementation.toml` is the exact 30-criterion Conductor
Polymath rubric (SHA-256
`8beb2c4a6faea2b5d673189b009e9a5f939eb717946372a8ace1fa475675868f`).
`rubrics/environment-integrity.toml` adds stricter evidence and task-time
provenance gates. They are complementary and should be run separately.

The installed Harbor 0.14 checkout includes a Codex backend for `harbor check`.
It runs Codex in an isolated ephemeral `CODEX_HOME`, ignores user rules/config,
uses a read-only sandbox, and accepts the existing Codex authentication. The
review commands are:

```sh
harbor check tasks/prometheus-subquery-semantics \
  --rubric .private-eval/rubrics/conductor-task-implementation.toml \
  --add-dir .private-eval --model openai/gpt-5.6-sol

harbor check tasks/prometheus-subquery-semantics \
  --rubric .private-eval/rubrics/environment-integrity.toml \
  --add-dir .private-eval --model openai/gpt-5.6-sol
```

Without reviewer-only bound runtime artifacts, runtime criteria must fail rather
than being inferred from expected outcomes or static solution scripts.

## Focused tests

```sh
python3 -m unittest discover -s .private-eval/tests -v
```

The synthetic tests cover draft-to-pinned binding, infrastructure
exception rejection, and unsafe candidate-archive link rejection.
