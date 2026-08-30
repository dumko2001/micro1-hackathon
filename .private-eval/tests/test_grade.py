from __future__ import annotations

import copy
import hashlib
import importlib.util
import io
import json
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "grade.py"
SPEC = importlib.util.spec_from_file_location("private_grade", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
grade = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = grade
SPEC.loader.exec_module(grade)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2))


def create_candidate(path: Path, link: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(path, "w:gz") as archive:
        root = tarfile.TarInfo("prometheus")
        root.type = tarfile.DIRTYPE
        root.mode = 0o755
        archive.addfile(root)
        if link:
            item = tarfile.TarInfo("prometheus/escape")
            item.type = tarfile.SYMTYPE
            item.linkname = "../../outside"
            archive.addfile(item)
        else:
            payload = b"package main\n"
            item = tarfile.TarInfo("prometheus/main.go")
            item.mode = 0o644
            item.size = len(payload)
            archive.addfile(item, io.BytesIO(payload))


def create_job(
    root: Path,
    exception: object = None,
    link: bool = False,
    verifier_status: str = "passed",
    reward: int = 1,
    agent_name: str = "oracle",
    agent_import_path: str | None = None,
    candidate_id: str | None = None,
) -> Path:
    job = root / "oracle-job"
    trial_name = "prometheus-subquery-semantics__abc1234"
    trial = job / trial_name
    candidate = trial / "artifacts/app/verifier-artifacts/candidate.tar.gz"
    sidecar = trial / "artifacts/app/verifier-artifacts/candidate.sha256"
    create_candidate(candidate, link=link)
    sidecar.write_text(f"{hashlib.sha256(candidate.read_bytes()).hexdigest()}  candidate.tar.gz\n")

    environment = {
        "type": "daytona",
        "delete": True,
        "override_cpus": 2,
        "override_memory_mb": 4096,
        "override_storage_mb": 10240,
    }
    agent = {"name": agent_name, "kwargs": {}}
    if agent_import_path is not None:
        agent = {"name": None, "import_path": agent_import_path, "kwargs": {}}
    if candidate_id is not None:
        agent["kwargs"]["candidate_id"] = candidate_id
    trial_config = {
        "task": {"path": "tasks/prometheus-subquery-semantics"},
        "trial_name": trial_name,
        "job_id": "11111111-1111-4111-8111-111111111111",
        "agent": agent,
        "environment": environment,
        # Harbor 0.14 does not copy task.toml-declared artifacts into this field.
        # The artifact manifest and collected files are authoritative.
        "artifacts": [],
    }
    trial_result = {
        "id": "22222222-2222-4222-8222-222222222222",
        "task_name": "prometheus-subquery-semantics",
        "trial_name": trial_name,
        "trial_uri": trial.as_uri(),
        "task_checksum": "a" * 64,
        "config": trial_config,
        "agent_info": {"name": agent_name, "version": "1.0.0", "model_info": None},
        "verifier_result": {"rewards": {"reward": float(reward)}},
        "exception_info": exception,
        "started_at": "2026-08-29T00:00:00Z",
        "finished_at": "2026-08-29T00:01:00Z",
    }
    job_lock = {
        "schema_version": 1,
        "harbor": {"version": "0.14.0"},
        "n_concurrent_trials": 5,
        "trials": [
            {
                "task": {
                    "name": "prometheus-subquery-semantics",
                    "type": "local",
                    "digest": "sha256:" + "b" * 64,
                },
                "agent": agent,
                "environment": environment,
            }
        ],
    }
    job_config = {
        "job_name": "oracle-job",
        "n_concurrent_trials": 5,
        "agents": [agent],
        "environment": environment,
    }
    job_result = {
        "id": "11111111-1111-4111-8111-111111111111",
        "started_at": "2026-08-29T00:00:00Z",
        "finished_at": "2026-08-29T00:01:00Z",
        "n_total_trials": 1,
        "stats": {
            "n_completed_trials": 1,
            "n_errored_trials": 0,
            "n_running_trials": 0,
            "n_pending_trials": 0,
            "n_cancelled_trials": 0,
            "evals": {
                "oracle__adhoc": {
                    "reward_stats": {"reward": {f"{float(reward):.1f}": [trial_name]}}
                }
            },
        },
    }
    artifact_manifest = [
        {
            "source": "/app/verifier-artifacts",
            "destination": "artifacts/app/verifier-artifacts",
            "type": "directory",
            "status": "ok",
        }
    ]
    write_json(job / "lock.json", job_lock)
    write_json(job / "config.json", job_config)
    write_json(job / "result.json", job_result)
    write_json(trial / "config.json", trial_config)
    write_json(trial / "result.json", trial_result)
    write_json(trial / "artifacts/manifest.json", artifact_manifest)
    if verifier_status == "passed":
        status_document = {"phase": "verify", "status": verifier_status, "reward": reward}
    else:
        # Mirrors a prepare-candidate failure: status has a reason but no reward field.
        status_document = {
            "phase": "source",
            "status": verifier_status,
            "reason": "workspace_override",
        }
    write_json(trial / "verifier/status.json", status_document)
    (trial / "verifier/reward.txt").write_text(f"{reward}\n")
    return job


def manifest() -> dict:
    return {
        "schema_version": 3,
        "gate": "test",
        "certifies": ["test"],
        "does_not_certify": [],
        "policy": {
            "harbor_version_prefix": "0.14.",
            "environment_type": "daytona",
            "require_environment_delete": True,
            "max_n_concurrent_trials": 5,
            "require_exact_resources": True,
            "resources": {"cpus": 2, "memory_mb": 4096, "storage_mb": 10240},
        },
        "evidence_bindings": {},
        "cases": [
            {
                "task": "step-invariant-subquery",
                "harbor_task": "prometheus-subquery-semantics",
                "id": "oracle",
                "label": "valid",
                "required_agent": "oracle",
                "required_reward": 1,
            }
        ],
    }


class GradeTests(unittest.TestCase):
    def test_emit_then_pinned_gate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            evidence = grade.discover([create_job(Path(directory))])
            draft, status = grade.evaluate(manifest(), evidence, emit_bindings=True)
            self.assertEqual(status, 0)
            self.assertFalse(draft["complete"])
            pinned = copy.deepcopy(manifest())
            pinned["evidence_bindings"] = draft["evidence_bindings"]
            report, status = grade.evaluate(pinned, evidence, emit_bindings=False)
            self.assertEqual(status, 0)
            self.assertTrue(report["complete"])

    def test_exception_never_becomes_reward_zero(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            exception = {"exception_type": "EnvironmentStartError"}
            evidence = grade.discover([create_job(Path(directory), exception=exception)])
            report, status = grade.evaluate(manifest(), evidence, emit_bindings=True)
            self.assertEqual(status, 1)
            self.assertTrue(any("exception_info" in failure for failure in report["failures"]))

    def test_candidate_links_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            evidence = grade.discover([create_job(Path(directory), link=True)])
            report, status = grade.evaluate(manifest(), evidence, emit_bindings=True)
            self.assertEqual(status, 1)
            self.assertTrue(any("link or special" in failure for failure in report["failures"]))

    def test_oracle_requires_explicit_passed_status(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            evidence = grade.discover(
                [
                    create_job(
                        Path(directory),
                        verifier_status="invalid_candidate",
                        reward=0,
                    )
                ]
            )
            report, status = grade.evaluate(manifest(), evidence, emit_bindings=True)
            self.assertEqual(status, 1)
            self.assertTrue(
                any("expected reward 1, observed 0" in failure for failure in report["failures"])
            )
            self.assertTrue(
                any(
                    "requires verifier status 'passed', observed 'invalid_candidate'" in failure
                    for failure in report["failures"]
                )
            )

    def test_candidate_fixture_id_is_part_of_case_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            evidence = grade.discover(
                [
                    create_job(
                        Path(directory),
                        agent_name="candidate-fixture",
                        agent_import_path=(
                            "private_eval.candidate_agent:CandidateFixtureAgent"
                        ),
                        candidate_id="mutant-1",
                    )
                ]
            )
            candidate_manifest = manifest()
            case = candidate_manifest["cases"][0]
            case["required_agent"] = "candidate-fixture"
            case["required_agent_import_path"] = (
                "private_eval.candidate_agent:CandidateFixtureAgent"
            )
            case["required_candidate_id"] = "alternate-valid"
            report, status = grade.evaluate(
                candidate_manifest,
                evidence,
                emit_bindings=True,
            )
            self.assertEqual(status, 1)
            self.assertTrue(
                any("expected one matching trial, found 0" in failure for failure in report["failures"])
            )

    def test_required_job_name_is_part_of_case_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            evidence = grade.discover([create_job(Path(directory))])
            named_manifest = manifest()
            named_manifest["cases"][0]["required_job_name"] = "different-job"
            report, status = grade.evaluate(named_manifest, evidence, emit_bindings=True)
            self.assertEqual(status, 1)
            self.assertTrue(
                any("expected one matching trial, found 0" in failure for failure in report["failures"])
            )

    def test_explicit_superseded_trial_can_be_ignored_once(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            current_job = create_job(root / "current")
            old_job = create_job(root / "old")
            old_config_path = old_job / "config.json"
            old_config = json.loads(old_config_path.read_text())
            old_config["job_name"] = "superseded-job"
            write_json(old_config_path, old_config)
            old_trial = next(path for path in old_job.iterdir() if path.is_dir())
            old_result_path = old_trial / "result.json"
            old_result = json.loads(old_result_path.read_text())
            old_result["task_name"] = "superseded-task"
            write_json(old_result_path, old_result)

            ignored_manifest = manifest()
            ignored_manifest["ignored_evidence"] = [
                {
                    "job_name": "superseded-job",
                    "harbor_task": "superseded-task",
                    "reason": "replaced by final task bytes",
                }
            ]
            evidence = grade.discover([current_job, old_job])
            draft, status = grade.evaluate(ignored_manifest, evidence, emit_bindings=True)
            self.assertEqual(status, 0)
            self.assertFalse(draft["failures"])


if __name__ == "__main__":
    unittest.main()
