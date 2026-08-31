# Prometheus environment contract

## Episode model

Each task follows the same lifecycle:

1. Extract a checksum-pinned clean-parent archive.
2. Give a stock coding agent one outcome-focused request.
3. Let the agent inspect, edit, build, and test as a non-root user.
4. Stop at completion, timeout, or environment failure.
5. Stop surviving actor processes, freeze the source, and collect a root-owned archive.
6. Destroy the actor container.
7. Run the task's verifier in a separate no-network environment.
8. Emit structured status and a binary reward.

The action space is normal terminal interaction through a Harbor coding-agent adapter. Observations are repository files and command output. Reward is `1` only when every mandatory gate passes. A valid but incorrect candidate receives `0`; an infrastructure failure receives no task reward.

This supports rollout collection and terminal-reward evaluation. It does not claim an online RL training API or a particular optimization algorithm.

## Ownership

The reusable environment owns the pinned Go image, safe archive extraction, build caches, generic build commands, and process controls.

Each task owns its clean parent, archive checksum, prompt, budget, exact reference stack, verifier cases, reward definition, and calibration evidence. Separate tasks may share a runtime but never assume the same source revision.

## Actor boundary

Actor source contains no `.git`, remotes, commit metadata, reference patch, solution script, hidden test, or verifier source. The model actor needs public egress to reach its provider. The instruction against online-solution lookup is enforceable as benchmark policy, not as network isolation.

The collect hook stops actor-owned processes, freezes the source tree, recreates the artifact directory as root, and invokes absolute system binaries. The verifier rejects unsafe archives, path escapes, special files, excessive expansion, unexpected workspaces or vendoring, and root-module drift.

## Verifier boundary

The verifier deletes candidate tests, restores trusted harness files, and compiles with workspace mode disabled. Candidate executables run as UID 65532 with an empty environment, no capabilities, `no_new_privs`, and resource limits. Build inputs are removed before execution where the gate permits it.

Verification uses the most external stable surface available:

- UDS and subquery tasks: a trusted controller drives a candidate Prometheus daemon.
- WAL expiry: a candidate program writes checkpoints that a trusted clean-parent reader inspects.
- Histogram: an external API controller is conjunctive with a linked Go breadth test.
- Start timestamp: a candidate writer creates normal and out-of-order lifecycles, the controller projects and seals valid blocks, and a candidate reader must return every sample field. A clean-parent writer supplies legacy blocks independently; no landed-format decoder or internal symbol is part of reward.

The linked histogram breadth gate remains weaker against malicious candidate code. Start timestamp keeps reward assertions in the root controller, but a deliberately colluding writer and reader could still fabricate the randomized protocol. Sealed read-only projections and process hardening close demonstrated bypasses; they are not a formal hostile-code proof.

Verifier statuses are:

- `infrastructure_error`: the runtime or required artifact is missing; no reward;
- `invalid_candidate`: the archive or module boundary is unsafe; reward `0`;
- `candidate_build_failed`: trusted compilation failed; reward `0`;
- `behavioral_failure`: one or more mandatory behaviors failed; reward `0`;
- `passed`: every mandatory gate passed; reward `1`.

## Release gates

A task is release-ready only after:

- deterministic source/generated parity;
- exact source checksum and first-parent lineage;
- clean Linux image build;
- clean parent fails and exact reference passes;
- no-op fails on identical bytes;
- an alternate-valid candidate passes;
- named mutants fail;
- repeated backend runs keep the same reward and status;
- infrastructure and candidate failures remain distinct;
- stock-agent calibration records solve rate, runtime, token use, and cost;
- public and secret evaluator artifacts have separate release boundaries.

The suite clears every listed verifier gate on its registered candidate set. Ten fixed-model stock rollouts finished: UDS, subquery, WAL, and start timestamp passed twice; histogram produced two semantic misses. This is difficulty evidence, not a claim of universal method neutrality or formal malicious-code resistance.
