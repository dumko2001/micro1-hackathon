#!/usr/bin/env python3
"""Fail-closed Harbor 0.14 evidence gate for private calibration artifacts.

The grader consumes completed Harbor job directories directly. It never trusts a
caller-authored reward receipt and never extracts candidate archives onto disk.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tarfile
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import unquote, urlparse
from uuid import UUID


ROOT = Path(__file__).resolve().parent
MAX_ARCHIVE_MEMBERS = 250_000
MAX_ARCHIVE_BYTES = 4 * 1024 * 1024 * 1024


class EvidenceError(ValueError):
    """Evidence is missing, ambiguous, unsafe, or internally inconsistent."""


@dataclass(frozen=True)
class TrialEvidence:
    job_dir: Path
    trial_dir: Path
    job_lock_path: Path
    job_config_path: Path
    job_result_path: Path
    trial_config_path: Path
    trial_result_path: Path
    artifact_manifest_path: Path
    verifier_status_path: Path
    verifier_reward_path: Path
    candidate_path: Path
    candidate_sidecar_path: Path
    job_lock: dict[str, Any]
    job_config: dict[str, Any]
    job_result: dict[str, Any]
    trial_config: dict[str, Any]
    trial_result: dict[str, Any]
    artifact_manifest: Any
    verifier_status: dict[str, Any]
    verifier_reward: int


def json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise EvidenceError(f"cannot read JSON {path}: {error}") from error
    if not isinstance(value, dict):
        raise EvidenceError(f"expected a JSON object: {path}")
    return value


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def confined_file(root: Path, path: Path, description: str) -> Path:
    root = root.resolve()
    lexical = Path(os.path.abspath(path))
    try:
        relative = lexical.relative_to(root)
    except ValueError as error:
        raise EvidenceError(f"{description} escapes trial directory: {path}") from error
    cursor = root
    for part in relative.parts:
        cursor /= part
        if cursor.is_symlink():
            raise EvidenceError(f"{description} traverses a symlink: {cursor}")
    candidate = path.resolve()
    if candidate == root or root not in candidate.parents:
        raise EvidenceError(f"{description} escapes trial directory: {path}")
    if not candidate.is_file():
        raise EvidenceError(f"{description} is not a regular file: {path}")
    return candidate


def normalized_archive_path(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if not name or path.is_absolute() or ".." in path.parts or "\x00" in name:
        raise EvidenceError(f"unsafe archive member path: {name!r}")
    parts = tuple(part for part in path.parts if part not in ("", "."))
    if not parts:
        raise EvidenceError(f"empty archive member path: {name!r}")
    return PurePosixPath(*parts)


def candidate_tree_hash(path: Path) -> str:
    """Hash canonical file-tree contents while rejecting unsafe tar semantics.

    Timestamps, owners, gzip headers, and archive order are ignored. A single
    common archive root (normally ``prometheus/``) is stripped. Paths,
    executable bits, sizes, and contents remain significant. Links, special
    entries, duplicate paths, traversal, and decompression bombs are rejected.
    """

    records: list[tuple[PurePosixPath, int, int, str]] = []
    seen: set[PurePosixPath] = set()
    total_size = 0
    with tarfile.open(path, mode="r:*") as archive:
        members = archive.getmembers()
        if len(members) > MAX_ARCHIVE_MEMBERS:
            raise EvidenceError("candidate archive has too many members")
        paths = [normalized_archive_path(member.name) for member in members]
        if len(set(paths)) != len(paths):
            raise EvidenceError("candidate archive contains duplicate member paths")
        roots = {member.parts[0] for member in paths}
        strip_root = len(roots) == 1 and all(
            member.isdir() or len(normalized.parts) > 1
            for member, normalized in zip(members, paths, strict=True)
        )
        for member, normalized in zip(members, paths, strict=True):
            relative = PurePosixPath(*normalized.parts[1:]) if strip_root else normalized
            if member.isdir():
                continue
            if not member.isfile():
                raise EvidenceError(
                    f"candidate archive contains a link or special member: {member.name!r}"
                )
            if relative in seen:
                raise EvidenceError(f"duplicate candidate archive path: {relative}")
            seen.add(relative)
            if member.size < 0:
                raise EvidenceError(f"negative candidate member size: {relative}")
            total_size += member.size
            if total_size > MAX_ARCHIVE_BYTES:
                raise EvidenceError("candidate archive expands beyond the safety limit")
            stream = archive.extractfile(member)
            if stream is None:
                raise EvidenceError(f"cannot read candidate member: {relative}")
            digest = hashlib.sha256()
            observed_size = 0
            while True:
                chunk = stream.read(1024 * 1024)
                if not chunk:
                    break
                observed_size += len(chunk)
                if observed_size > member.size:
                    raise EvidenceError(f"candidate member exceeds declared size: {relative}")
                digest.update(chunk)
            if observed_size != member.size:
                raise EvidenceError(f"candidate member size mismatch: {relative}")
            records.append((relative, member.mode & 0o111, member.size, digest.hexdigest()))

    if not records:
        raise EvidenceError("candidate archive contains no regular files")
    tree = hashlib.sha256()
    for relative, executable, size, digest in sorted(records, key=lambda item: str(item[0])):
        tree.update(f"file\0{relative}\0{executable:o}\0{size}\0{digest}\n".encode())
    return tree.hexdigest()


def manifest_entries(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        value = value.get("entries")
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise EvidenceError("artifact manifest must be a list or an object with an entries list")
    return value


def artifact_from_manifest(
    trial_dir: Path, entries: list[dict[str, Any]], source: str
) -> Path:
    source_path = PurePosixPath(source)
    matches: list[Path] = []
    for entry in entries:
        if entry.get("status") != "ok":
            continue
        entry_source_raw = entry.get("source")
        destination_raw = entry.get("destination")
        if not isinstance(entry_source_raw, str) or not isinstance(destination_raw, str):
            continue
        entry_source = PurePosixPath(entry_source_raw)
        try:
            suffix = source_path.relative_to(entry_source)
        except ValueError:
            continue
        destination = Path(destination_raw)
        if destination.is_absolute():
            continue
        matches.append(confined_file(trial_dir, trial_dir / destination / Path(*suffix.parts), source))
    unique = {path.resolve(): path for path in matches}
    if len(unique) != 1:
        raise EvidenceError(f"artifact {source!r} has {len(unique)} successful manifest mappings")
    return next(iter(unique.values()))


def load_trial(job_dir: Path, trial_dir: Path) -> TrialEvidence:
    job_dir = job_dir.resolve()
    trial_dir = trial_dir.resolve()
    paths = {
        "job_lock_path": confined_file(job_dir, job_dir / "lock.json", "job lock"),
        "job_config_path": confined_file(job_dir, job_dir / "config.json", "job config"),
        "job_result_path": confined_file(job_dir, job_dir / "result.json", "job result"),
        "trial_config_path": confined_file(trial_dir, trial_dir / "config.json", "trial config"),
        "trial_result_path": confined_file(trial_dir, trial_dir / "result.json", "trial result"),
        "artifact_manifest_path": confined_file(
            trial_dir, trial_dir / "artifacts/manifest.json", "artifact manifest"
        ),
        "verifier_status_path": confined_file(
            trial_dir, trial_dir / "verifier/status.json", "verifier status"
        ),
        "verifier_reward_path": confined_file(
            trial_dir, trial_dir / "verifier/reward.txt", "verifier reward"
        ),
    }
    try:
        artifact_manifest_value = json.loads(paths["artifact_manifest_path"].read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise EvidenceError(f"cannot read artifact manifest: {error}") from error
    entries = manifest_entries(artifact_manifest_value)
    verifier_status = json_object(paths["verifier_status_path"])
    reward_text = paths["verifier_reward_path"].read_text().strip()
    if reward_text not in {"0", "0.0", "1", "1.0"}:
        raise EvidenceError(f"verifier reward.txt is not binary: {reward_text!r}")
    verifier_reward = int(float(reward_text))
    candidate_path = artifact_from_manifest(
        trial_dir, entries, "/app/verifier-artifacts/candidate.tar.gz"
    )
    sidecar_path = artifact_from_manifest(
        trial_dir, entries, "/app/verifier-artifacts/candidate.sha256"
    )
    return TrialEvidence(
        job_dir=job_dir,
        trial_dir=trial_dir,
        candidate_path=candidate_path,
        candidate_sidecar_path=sidecar_path,
        job_lock=json_object(paths["job_lock_path"]),
        job_config=json_object(paths["job_config_path"]),
        job_result=json_object(paths["job_result_path"]),
        trial_config=json_object(paths["trial_config_path"]),
        trial_result=json_object(paths["trial_result_path"]),
        artifact_manifest=artifact_manifest_value,
        verifier_status=verifier_status,
        verifier_reward=verifier_reward,
        **paths,
    )


def discover(job_dirs: Iterable[Path]) -> list[TrialEvidence]:
    evidence: list[TrialEvidence] = []
    seen_jobs: set[Path] = set()
    for supplied in job_dirs:
        if supplied.is_symlink():
            raise EvidenceError(f"job directory is a symlink: {supplied}")
        job_dir = supplied.resolve()
        if job_dir in seen_jobs:
            raise EvidenceError(f"duplicate job directory: {supplied}")
        seen_jobs.add(job_dir)
        if not all((job_dir / name).is_file() for name in ("lock.json", "config.json", "result.json")):
            raise EvidenceError(f"not a completed Harbor job directory: {supplied}")
        trial_dirs = sorted(
            child
            for child in job_dir.iterdir()
            if child.is_dir()
            and not child.is_symlink()
            and (child / "config.json").is_file()
            and (child / "result.json").is_file()
        )
        if not trial_dirs:
            raise EvidenceError(f"job has no completed trial directories: {supplied}")
        evidence.extend(load_trial(job_dir, trial_dir) for trial_dir in trial_dirs)
    return evidence


def value_at(value: Any, *path: str) -> Any:
    current = value
    for component in path:
        if not isinstance(current, dict):
            return None
        current = current.get(component)
    return current


def numeric_reward(result: dict[str, Any]) -> int | None:
    rewards = value_at(result, "verifier_result", "rewards")
    if not isinstance(rewards, dict) or set(rewards) != {"reward"}:
        return None
    reward = rewards["reward"]
    if isinstance(reward, bool) or reward not in (0, 0.0, 1, 1.0):
        return None
    return int(reward)


def matching_lock_trials(
    evidence: TrialEvidence,
    task_name: str,
    agent_name: str | None = None,
    agent_import_path: str | None = None,
) -> list[dict[str, Any]]:
    trials = evidence.job_lock.get("trials")
    if not isinstance(trials, list):
        return []
    return [
        trial
        for trial in trials
        if isinstance(trial, dict)
        and value_at(trial, "task", "name") == task_name
        and (
            agent_import_path is None
            or value_at(trial, "agent", "import_path") == agent_import_path
        )
        and (
            agent_name is None
            or agent_import_path is not None
            or value_at(trial, "agent", "name") == agent_name
        )
    ]


def binding_for(evidence: TrialEvidence, lock_trial: dict[str, Any]) -> dict[str, Any]:
    return {
        "job_id": str(evidence.job_result.get("id")),
        "trial_id": str(evidence.trial_result.get("id")),
        "trial_name": evidence.trial_result.get("trial_name"),
        "job_lock_sha256": file_hash(evidence.job_lock_path),
        "job_config_sha256": file_hash(evidence.job_config_path),
        "job_result_sha256": file_hash(evidence.job_result_path),
        "trial_config_sha256": file_hash(evidence.trial_config_path),
        "trial_result_sha256": file_hash(evidence.trial_result_path),
        "artifact_manifest_sha256": file_hash(evidence.artifact_manifest_path),
        "verifier_status_sha256": file_hash(evidence.verifier_status_path),
        "verifier_reward_sha256": file_hash(evidence.verifier_reward_path),
        "candidate_archive_sha256": file_hash(evidence.candidate_path),
        "candidate_tree_sha256": candidate_tree_hash(evidence.candidate_path),
        "task_digest": value_at(lock_trial, "task", "digest"),
        "task_checksum": evidence.trial_result.get("task_checksum"),
    }


def uri_trial_name(uri: Any) -> str | None:
    if not isinstance(uri, str):
        return None
    parsed = urlparse(uri)
    return Path(unquote(parsed.path)).name if parsed.scheme == "file" else None


def valid_uuid(value: Any) -> bool:
    try:
        UUID(str(value))
    except (ValueError, TypeError, AttributeError):
        return False
    return True


def validate_case(
    case: dict[str, Any], evidence: TrialEvidence, policy: dict[str, Any]
) -> tuple[list[str], dict[str, Any]]:
    failures: list[str] = []
    task_name = case.get("harbor_task")
    expected_agent = case.get("required_agent")
    expected_agent_import = case.get("required_agent_import_path")
    trial = evidence.trial_result
    config = evidence.trial_config
    job = evidence.job_result
    job_config = evidence.job_config
    job_id = str(job.get("id"))
    trial_name = trial.get("trial_name")

    if evidence.job_lock.get("schema_version") != 1:
        failures.append("unsupported Harbor job lock schema_version")
    required_harbor = policy.get("harbor_version_prefix")
    observed_harbor = value_at(evidence.job_lock, "harbor", "version")
    if required_harbor and (
        not isinstance(observed_harbor, str) or not observed_harbor.startswith(required_harbor)
    ):
        failures.append(
            f"Harbor version {observed_harbor!r} does not match prefix {required_harbor!r}"
        )
    if not valid_uuid(job.get("id")) or not valid_uuid(trial.get("id")):
        failures.append("job or trial id is not a UUID")
    if job_config.get("job_name") != evidence.job_dir.name:
        failures.append("job config name does not match the job directory")

    if trial.get("task_name") != task_name:
        failures.append("trial result task_name mismatch")
    if config != trial.get("config"):
        failures.append("trial result does not embed the parsed trial config")
    if config.get("trial_name") != trial_name or evidence.trial_dir.name != trial_name:
        failures.append("trial directory/config/result names are not cross-linked")
    if uri_trial_name(trial.get("trial_uri")) != trial_name:
        failures.append("trial_uri does not identify the trial directory")
    if str(config.get("job_id")) != job_id:
        failures.append("trial config job_id does not match job result id")
    if job.get("finished_at") is None or trial.get("finished_at") is None:
        failures.append("job or trial is not terminal")
    if not isinstance(job.get("n_total_trials"), int) or job.get("n_total_trials") < 1:
        failures.append("job n_total_trials is missing or invalid")
    if trial.get("exception_info") is not None:
        failures.append("trial has exception_info")
    if expected_agent and value_at(trial, "agent_info", "name") != expected_agent:
        failures.append("trial agent_info does not match required agent")
    if expected_agent_import:
        if value_at(config, "agent", "import_path") != expected_agent_import:
            failures.append("trial config does not match required agent import path")
    elif expected_agent and value_at(config, "agent", "name") != expected_agent:
        failures.append("trial config does not match required agent")
    configured_agents = job_config.get("agents")
    if expected_agent and (
        not isinstance(configured_agents, list)
        or not any(
            isinstance(agent, dict)
            and (
                agent.get("import_path") == expected_agent_import
                if expected_agent_import
                else agent.get("name") == expected_agent
            )
            for agent in configured_agents
        )
    ):
        failures.append("job config does not contain the required agent")

    stats = job.get("stats")
    if not isinstance(stats, dict):
        failures.append("job stats are missing")
    else:
        for field in ("n_errored_trials", "n_running_trials", "n_pending_trials", "n_cancelled_trials"):
            if stats.get(field) != 0:
                failures.append(f"job {field} must be zero")
        if stats.get("n_completed_trials") != job.get("n_total_trials"):
            failures.append("job completion count does not match n_total_trials")

    lock_trials = matching_lock_trials(
        evidence,
        str(task_name),
        expected_agent,
        expected_agent_import,
    )
    if len(lock_trials) != 1:
        failures.append(f"job lock has {len(lock_trials)} matching task entries")
        lock_trial: dict[str, Any] = {}
    else:
        lock_trial = lock_trials[0]
    if expected_agent_import:
        if value_at(lock_trial, "agent", "import_path") != expected_agent_import:
            failures.append("job lock does not match required agent import path")
    elif expected_agent and value_at(lock_trial, "agent", "name") != expected_agent:
        failures.append("job lock does not match required agent")

    max_concurrency = policy.get("max_n_concurrent_trials")
    concurrency = evidence.job_lock.get("n_concurrent_trials")
    if not isinstance(concurrency, int) or concurrency < 1:
        failures.append("job lock concurrency is missing or invalid")
    elif isinstance(max_concurrency, int) and concurrency > max_concurrency:
        failures.append(f"job concurrency {concurrency} exceeds {max_concurrency}")
    if job_config.get("n_concurrent_trials") != concurrency:
        failures.append("job config and lock concurrency differ")

    required_environment = policy.get("environment_type")
    config_environment = value_at(config, "environment", "type")
    lock_environment = value_at(lock_trial, "environment", "type")
    if required_environment and (
        config_environment != required_environment or lock_environment != required_environment
    ):
        failures.append(f"environment is not consistently {required_environment!r}")
    if required_environment and value_at(job_config, "environment", "type") != required_environment:
        failures.append("job config environment type does not match policy")
    if policy.get("require_environment_delete", True):
        for label, environment in (
            ("job config", value_at(job_config, "environment")),
            ("trial config", value_at(config, "environment")),
            ("job lock", value_at(lock_trial, "environment")),
        ):
            if not isinstance(environment, dict) or environment.get("delete") is not True:
                failures.append(f"{label} does not require sandbox deletion")

    resources = policy.get("resources")
    if isinstance(resources, dict):
        fields = {
            "cpus": "override_cpus",
            "memory_mb": "override_memory_mb",
            "storage_mb": "override_storage_mb",
        }
        exact = bool(policy.get("require_exact_resources", True))
        for public_name, field in fields.items():
            required = resources.get(public_name)
            for label, environment in (
                ("job config", value_at(job_config, "environment")),
                ("trial config", value_at(config, "environment")),
                ("job lock", value_at(lock_trial, "environment")),
            ):
                observed = environment.get(field) if isinstance(environment, dict) else None
                if exact and observed != required:
                    failures.append(f"{label} {field} must equal {required}, observed {observed}")
                elif not exact and (not isinstance(observed, int) or observed > required):
                    failures.append(f"{label} {field} exceeds or omits cap {required}")

    raw_archive_hash = file_hash(evidence.candidate_path)
    sidecar_parts = evidence.candidate_sidecar_path.read_text().strip().split()
    if not sidecar_parts or sidecar_parts[0].lower() != raw_archive_hash:
        failures.append("candidate.sha256 does not bind candidate.tar.gz")
    task_digest = value_at(lock_trial, "task", "digest")
    task_checksum = trial.get("task_checksum")
    if not isinstance(task_digest, str) or not task_digest.startswith("sha256:") or len(task_digest) != 71:
        failures.append("job lock task digest is not a sha256 digest")
    if not isinstance(task_checksum, str) or len(task_checksum) != 64 or any(
        char not in "0123456789abcdef" for char in task_checksum
    ):
        failures.append("trial task_checksum is not a lowercase sha256 digest")

    actual_reward = numeric_reward(trial)
    if actual_reward is None:
        failures.append("verifier reward is missing, non-binary, or has unexpected reward keys")
    elif actual_reward != case.get("required_reward"):
        failures.append(f"expected reward {case.get('required_reward')}, observed {actual_reward}")
    verifier_status = evidence.verifier_status.get("status")
    status_reward = evidence.verifier_status.get("reward")
    if actual_reward is not None and evidence.verifier_reward != actual_reward:
        failures.append(
            f"verifier reward.txt {evidence.verifier_reward} contradicts TrialResult {actual_reward}"
        )
    if status_reward is not None and (
        isinstance(status_reward, bool) or status_reward not in (0, 0.0, 1, 1.0)
    ):
        failures.append("verifier status.json reward is non-binary")
    elif status_reward is not None and actual_reward is not None and int(status_reward) != actual_reward:
        failures.append("verifier status.json reward contradicts TrialResult")
    if verifier_status == "passed" and actual_reward != 1:
        failures.append("verifier status 'passed' requires reward one")
    if verifier_status in {
        "behavioral_failure",
        "candidate_build_failed",
        "invalid_candidate",
    } and actual_reward != 0:
        failures.append(f"verifier status {verifier_status!r} requires reward zero")
    if verifier_status in {"passed", "behavioral_failure", "candidate_build_failed"} and status_reward is None:
        failures.append(f"verifier status {verifier_status!r} must bind reward in status.json")
    if case.get("label") == "valid":
        if verifier_status != "passed":
            failures.append(
                f"valid/oracle case requires verifier status 'passed', observed {verifier_status!r}"
            )
    elif verifier_status not in {
        "behavioral_failure",
        "candidate_build_failed",
        "invalid_candidate",
    }:
        failures.append(
            "invalid/no-op case requires behavioral or candidate failure status, "
            f"observed {verifier_status!r}"
        )
    if isinstance(stats, dict) and actual_reward is not None:
        references = 0
        evals = stats.get("evals")
        if isinstance(evals, dict):
            for evaluation in evals.values():
                reward_stats = value_at(evaluation, "reward_stats", "reward")
                if not isinstance(reward_stats, dict):
                    continue
                for reward_key, names in reward_stats.items():
                    if isinstance(names, list) and trial_name in names:
                        try:
                            aggregate_reward = float(reward_key)
                        except (TypeError, ValueError):
                            aggregate_reward = float("nan")
                        if aggregate_reward == float(actual_reward):
                            references += 1
                        else:
                            failures.append("job aggregate records a contradictory trial reward")
        if references != 1:
            failures.append(f"job aggregate contains {references} matching reward references")

    try:
        binding = binding_for(evidence, lock_trial)
    except (OSError, tarfile.TarError, EvidenceError) as error:
        failures.append(f"candidate evidence is invalid: {error}")
        binding = {}
    return failures, binding


def evidence_matches_case(case: dict[str, Any], evidence: TrialEvidence) -> bool:
    expected_candidate = case.get("required_candidate_id")
    expected_job_name = case.get("required_job_name")
    observed_candidate = value_at(
        evidence.trial_result,
        "config",
        "agent",
        "kwargs",
        "candidate_id",
    )
    return (
        evidence.trial_result.get("task_name") == case.get("harbor_task")
        and (not expected_job_name or evidence.job_config.get("job_name") == expected_job_name)
        and (
            not case.get("required_agent")
            or value_at(evidence.trial_result, "agent_info", "name") == case.get("required_agent")
        )
        and (not expected_candidate or observed_candidate == expected_candidate)
    )


def rates(records: list[tuple[str, int, int]]) -> dict[str, float | None]:
    valid = [(expected, actual) for label, expected, actual in records if label == "valid"]
    invalid = [(expected, actual) for label, expected, actual in records if label == "invalid"]
    tpr = sum(actual == 1 for _, actual in valid) / len(valid) if valid else 0.0
    tnr = sum(actual == 0 for _, actual in invalid) / len(invalid) if invalid else 0.0
    return {
        "balanced_accuracy": (tpr + tnr) / 2,
        "false_accept_rate": (sum(actual != 0 for _, actual in invalid) / len(invalid)) if invalid else None,
        "false_reject_rate": (sum(actual != 1 for _, actual in valid) / len(valid)) if valid else None,
    }


def evaluate(
    manifest: dict[str, Any], evidence: list[TrialEvidence], emit_bindings: bool
) -> tuple[dict[str, Any], int]:
    failures: list[str] = []
    cases = manifest.get("cases")
    bindings = manifest.get("evidence_bindings")
    ignored_evidence = manifest.get("ignored_evidence", [])
    policy = manifest.get("policy")
    if not isinstance(cases, list) or not all(isinstance(case, dict) for case in cases):
        cases = []
        failures.append("manifest cases must be a list of objects")
    if not isinstance(bindings, dict):
        bindings = {}
        failures.append("manifest evidence_bindings must be an object")
    if not isinstance(ignored_evidence, list) or not all(
        isinstance(item, dict) for item in ignored_evidence
    ):
        ignored_evidence = []
        failures.append("manifest ignored_evidence must be a list of objects")
    if not isinstance(policy, dict):
        policy = {}
        failures.append("manifest policy must be an object")

    if manifest.get("schema_version") != 3:
        failures.append("manifest schema_version must be 3")
    expected_keys: set[str] = set()
    for case in cases:
        key = f"{case.get('task')}/{case.get('id')}"
        if key in expected_keys:
            failures.append(f"duplicate manifest case: {key}")
        expected_keys.add(key)
        if not all(isinstance(case.get(field), str) and case.get(field) for field in ("task", "harbor_task", "id")):
            failures.append(f"{key}: task, harbor_task, and id must be non-empty strings")
        if case.get("label") not in {"valid", "invalid"}:
            failures.append(f"{key}: label must be valid or invalid")
        if isinstance(case.get("required_reward"), bool) or case.get("required_reward") not in (0, 1):
            failures.append(f"{key}: required_reward must be binary")
    extra_bindings = sorted(set(bindings) - expected_keys)
    if extra_bindings:
        failures.append(f"manifest has unexpected evidence bindings: {extra_bindings}")
    ignored_keys: set[tuple[str, str]] = set()
    for ignored in ignored_evidence:
        job_name = ignored.get("job_name")
        task_name = ignored.get("harbor_task")
        reason = ignored.get("reason")
        if not all(isinstance(value, str) and value for value in (job_name, task_name, reason)):
            failures.append("ignored evidence requires non-empty job_name, harbor_task, and reason")
            continue
        key = (job_name, task_name)
        if key in ignored_keys:
            failures.append(f"duplicate ignored evidence rule: {key}")
        ignored_keys.add(key)

    used: set[tuple[Path, Path]] = set()
    emitted: dict[str, Any] = {}
    overall: list[tuple[str, int, int]] = []
    by_task: dict[str, list[tuple[str, int, int]]] = defaultdict(list)
    for case in cases:
        key = f"{case.get('task')}/{case.get('id')}"
        pinned = bindings.get(key)
        candidates = [item for item in evidence if evidence_matches_case(case, item)]
        if isinstance(pinned, dict) and not emit_bindings:
            candidates = [
                item
                for item in candidates
                if str(item.job_result.get("id")) == pinned.get("job_id")
                and str(item.trial_result.get("id")) == pinned.get("trial_id")
            ]
        elif not emit_bindings:
            failures.append(f"{key}: immutable evidence binding is missing")
            continue
        if len(candidates) != 1:
            failures.append(f"{key}: expected one matching trial, found {len(candidates)}")
            continue
        item = candidates[0]
        identity = (item.job_dir, item.trial_dir)
        if identity in used:
            failures.append(f"{key}: trial is reused by another case")
            continue
        used.add(identity)
        case_failures, observed_binding = validate_case(case, item, policy)
        failures.extend(f"{key}: {failure}" for failure in case_failures)
        emitted[key] = observed_binding
        if isinstance(pinned, dict) and not emit_bindings:
            for field, observed in observed_binding.items():
                if pinned.get(field) != observed:
                    failures.append(f"{key}: {field} does not match pinned evidence")
            extra_fields = sorted(set(pinned) - set(observed_binding))
            if extra_fields:
                failures.append(f"{key}: pinned evidence has unknown fields {extra_fields}")
        reward = numeric_reward(item.trial_result)
        if reward is not None:
            expected_reward = case.get("required_reward")
            if expected_reward in (0, 1) and not isinstance(expected_reward, bool):
                record = (str(case.get("label")), int(expected_reward), reward)
            else:
                continue
            overall.append(record)
            by_task[str(case.get("task"))].append(record)

    ignored_matches: dict[tuple[str, str], int] = defaultdict(int)
    unused: list[str] = []
    for item in evidence:
        if (item.job_dir, item.trial_dir) in used:
            continue
        ignore_key = (
            str(item.job_config.get("job_name", "")),
            str(item.trial_result.get("task_name", "")),
        )
        if ignore_key in ignored_keys:
            ignored_matches[ignore_key] += 1
        else:
            unused.append(str(item.trial_dir))
    unused.sort()
    if unused:
        failures.append(f"unexpected completed trials: {unused}")
    for ignored_key in sorted(ignored_keys):
        if ignored_matches[ignored_key] != 1:
            failures.append(
                f"ignored evidence rule {ignored_key} matched {ignored_matches[ignored_key]} trials"
            )

    report = {
        "complete": not failures and not emit_bindings,
        "gate": manifest.get("gate"),
        "certifies": manifest.get("certifies", []),
        "does_not_certify": manifest.get("does_not_certify", []),
        "overall": rates(overall),
        "by_task": {task: rates(records) for task, records in sorted(by_task.items())},
        "failures": failures,
    }
    if emit_bindings:
        report["complete"] = False
        report["binding_candidate_only"] = True
        report["evidence_bindings"] = emitted
        report["note"] = (
            "Review and pin these bindings in the private manifest, then rerun "
            "without --emit-bindings."
        )
    return report, 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job_dirs", nargs="+", type=Path, help="completed Harbor 0.14 job directories")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "cases/runtime-smoke-manifest.json",
        help="private case manifest (defaults to the separate oracle/no-op smoke gate)",
    )
    parser.add_argument(
        "--emit-bindings",
        action="store_true",
        help="validate unpinned jobs and print candidate bindings; never certifies or edits the manifest",
    )
    parser.add_argument(
        "--pin-bindings",
        action="store_true",
        help="author-only: validate an unpinned corpus and atomically pin its exact native evidence",
    )
    args = parser.parse_args()
    if args.emit_bindings and args.pin_bindings:
        parser.error("--emit-bindings and --pin-bindings are mutually exclusive")
    try:
        manifest = json_object(args.manifest.resolve())
        evidence = discover(args.job_dirs)
        report, status = evaluate(manifest, evidence, args.emit_bindings or args.pin_bindings)
        if args.pin_bindings:
            if status != 0 or report.get("failures"):
                raise EvidenceError("refusing to pin evidence that did not validate cleanly")
            bindings = report.get("evidence_bindings")
            if not isinstance(bindings, dict) or len(bindings) != len(manifest.get("cases", [])):
                raise EvidenceError("refusing to pin an incomplete evidence set")
            manifest["evidence_bindings"] = bindings
            manifest_path = args.manifest.resolve()
            with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", dir=manifest_path.parent, delete=False
            ) as handle:
                json.dump(manifest, handle, indent=2)
                handle.write("\n")
                temporary = Path(handle.name)
            os.replace(temporary, manifest_path)
            report = {
                "complete": False,
                "gate": manifest.get("gate"),
                "pinned_cases": len(bindings),
                "manifest": str(manifest_path),
                "note": "Bindings were pinned atomically; rerun without --pin-bindings to certify.",
            }
    except (OSError, json.JSONDecodeError, tarfile.TarError, EvidenceError) as error:
        report = {"complete": False, "failures": [str(error)]}
        status = 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
