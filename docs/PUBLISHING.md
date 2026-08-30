# Publishing the suite

## Current state

This checkout is not public. It has local commit `8cc0415` and no configured remote. Final Oracle-alignment edits remain uncommitted.

The tree contains both sides of the evaluation boundary:

- generated Harbor tasks and agent instructions;
- bundled clean-parent source archives;
- reference patches and `solve.sh` scripts;
- verifier cases and trusted fixtures;
- reviewer calibration code, candidate fixtures, manifests, and rubric outputs, which are tracked in this transparent authoring repository;
- credentials, raw `jobs/` output, and recordings, which remain excluded by `.gitignore`.

All five bundled source archives are stripped of `.git`, remotes, and history. That prevents direct Git discovery inside the task checkout. It cannot stop an actor with public egress from identifying familiar code or searching online. A published authoring repository is also not secret: its reference patches and verifier cases are readable once pushed.

## Recommended release layout

Use two release boundaries.

### Public submission artifact

Publish the material needed to understand and reproduce the hackathon work:

- README, Improvement Changelog, reproduction guide, and evidence ledger;
- environment and materializer source;
- task instructions and provenance registry;
- the full solution bundle required by the judges;
- redacted representative trajectories;
- solution video link;
- license, notices, and release manifest.

Label this a transparent authoring and reproduction artifact. Do not describe it as a secret live benchmark.

### Private evaluation source

For later model evaluation, create a separate private repository or object-store boundary containing:

- unreleased verifier cases and mutants;
- oracle and alternate-valid implementations;
- calibration manifests and raw job evidence;
- deployment credentials supplied at runtime, never committed;
- generated evaluator packages whose access is limited to the runner.

A real secret benchmark should use fresh unreleased cases. Copying the current public tests into a private repository after publication does not restore secrecy.

If Micro1 judges need the complete source before a public release, share the full repository privately with them. The PDF requires access and reproducibility, not a public GitHub URL.

Share private calibration evidence through restricted repository access or an encrypted archive. Put the bundle's SHA-256 in the public release manifest so judges can confirm they reviewed the cited bytes without exposing the cases.

## Pre-publication checks

Before creating a remote:

1. commit the final Oracle-alignment edits and record the SHA in the submission;
2. run `git status --ignored` and confirm `.env`, `jobs/`, private submissions, and raw trajectories are ignored;
3. scan the staged tree for credentials, `auth.json`, private URLs, and personal paths;
4. decide whether the release is transparent or secrecy-preserving, then include or exclude solutions and verifier cases consistently;
5. add representative redacted trajectories for every agent used;
6. add the five-minute-or-shorter video link;
7. record the same-case baseline/final comparison, full results, runtime, token use, and cost;
8. review Prometheus and container dependency notices and produce an SBOM;
9. materialize from a clean clone and rerun the documented smoke commands;
10. give judges the exact commit, Harbor version, required credentials, and expected output.
