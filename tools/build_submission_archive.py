#!/usr/bin/env python3
"""Build the lean Micro1 source upload from the local evidence tree."""

from __future__ import annotations

import csv
import json
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "submission/micro1-source-code.zip"
ARCHIVE_ROOT = "micro1-submission"

ROOT_FILES = {
    ".env.example",
    "CHANGELOG.md",
    "LICENSE",
    "NOTICE",
    "README.md",
}

DOC_FILES = {
    "BUILD_LOG.md",
    "REPRODUCTION.md",
    "TASK_SUITE_EVIDENCE.md",
    "VERIFIER_PROVENANCE_AUDIT.md",
}

TOOL_FILES = {
    "build_submission_archive.py",
    "materialize_prometheus_task.py",
    "score_candidate_matrix.py",
}

OMITTED_SUPPORT_DOCS = {
    Path("task_support/prometheus/CONTRACT.md"),
    Path("task_support/prometheus/environment/README.md"),
    Path("task_support/prometheus/environment/profiles/README.md"),
}

OMITTED_FIXTURE_PARTS = {
    "r1-replay",
    "r2-replay",
    "mutant-3",
    "mutant-4",
    "mutant-5",
    "mutant-6",
    "mutant-7",
}

FINAL_FIXTURES = {
    "native-histogram-rate": {"alternate-valid", "mutant-1", "mutant-2"},
    "stale-series-wal-expiry": {"alternate-valid", "mutant-1", "mutant-2"},
    "start-timestamp-persistence": {"alternate-valid", "mutant-1", "mutant-2"},
    "step-invariant-subquery": {"alternate-valid", "mutant-1", "mutant-2"},
    "unix-socket-scraping": {"alternate-oracle-aligned", "mutant-1", "mutant-2"},
}

INITIAL_MAX_TRIALS = {
    "unix-socket-scraping__RCWX6EK",
    "unix-socket-scraping__RPggSkf",
    "prometheus-subquery-semantics__z6i3N4R",
    "prometheus-subquery-semantics__q5fRhhp",
    "histogram-rate-semantics__tgDmR5G",
    "histogram-rate-semantics__mbWUFyx",
    "stale-wal-expiry__sk7vQ7S",
    "stale-wal-expiry__VBwCqHT",
    "start-timestamp-persistence__KkAfVSK",
    "start-timestamp-persistence__TJwBFiw",
}


def selected_source_files() -> list[Path]:
    selected: set[Path] = set()
    for name in ROOT_FILES:
        selected.add(ROOT / name)
    for name in DOC_FILES:
        selected.add(ROOT / "docs" / name)
    for name in TOOL_FILES:
        selected.add(ROOT / "tools" / name)

    for path in (ROOT / "task_support").rglob("*"):
        relative = path.relative_to(ROOT)
        if (
            path.is_file()
            and relative not in OMITTED_SUPPORT_DOCS
            and not (path.name == "SOURCE.md" and "source" in path.parts)
        ):
            selected.add(path)

    for path in (ROOT / "private_eval").rglob("*.py"):
        if "__pycache__" not in path.parts:
            selected.add(path)

    private_root = ROOT / ".private-eval"
    selected.add(private_root / "cases/oracle-conformance-manifest.json")
    for path in (private_root / "candidates").rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(private_root / "candidates")
        if any(part in OMITTED_FIXTURE_PARTS for part in relative.parts):
            continue
        if len(relative.parts) < 2:
            continue
        task_name = relative.parts[0]
        fixture_name = relative.parts[1].removesuffix(".patch")
        if (
            fixture_name in FINAL_FIXTURES.get(task_name, set())
            and path.suffix in {".patch", ".sh"}
        ):
            selected.add(path)

    missing = sorted(path for path in selected if not path.is_file())
    if missing:
        raise FileNotFoundError("missing submission files: " + ", ".join(map(str, missing)))
    return sorted(selected)


def cohort_for(job_name: str, trial_name: str) -> str:
    if job_name.startswith("micro1-oracle-alignment-final-"):
        return "final-high-calibration"
    if job_name.startswith("micro1-current-luna-default-"):
        return "intermediate-high-calibration"
    if trial_name in INITIAL_MAX_TRIALS:
        return "initial-max-calibration"
    return "development-calibration"


def iso_duration_seconds(started_at: str | None, finished_at: str | None) -> float | None:
    if not started_at or not finished_at:
        return None
    start = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    finish = datetime.fromisoformat(finished_at.replace("Z", "+00:00"))
    return round((finish - start).total_seconds(), 3)


def reasoning_for(config: dict) -> str:
    value = config.get("agent", {}).get("kwargs", {}).get("reasoning_effort")
    return value or "default-high"


def sanitized_record(job_name: str, trial_dir: Path) -> dict:
    config_path = trial_dir / "config.json"
    result_path = trial_dir / "result.json"
    trajectory_path = trial_dir / "agent/trajectory.json"
    config = json.loads(config_path.read_text()) if config_path.is_file() else {}
    result = json.loads(result_path.read_text()) if result_path.is_file() else None

    record = {
        "job": job_name,
        "trial": trial_dir.name,
        "task": (result or {}).get("task_name") or trial_dir.name.rsplit("__", 1)[0],
        "cohort": cohort_for(job_name, trial_dir.name),
        "model": config.get("agent", {}).get("model_name", "gpt-5.6-luna"),
        "reasoning": reasoning_for(config),
        "trajectory_present": trajectory_path.is_file(),
        "terminal_result_present": result is not None,
        "status": "no-trajectory" if not trajectory_path.is_file() else "incomplete-no-result",
        "reward": None,
        "exception": None,
        "started_at": None,
        "finished_at": None,
        "elapsed_seconds": None,
        "agent_input_tokens": None,
        "agent_cached_tokens": None,
        "agent_output_tokens": None,
        "agent_cost_usd": None,
        "included_in_submission": False,
        "exclusion_reason": None,
    }
    if result is not None:
        reward = (result.get("verifier_result") or {}).get("rewards", {}).get("reward")
        exception = result.get("exception_info")
        status = "terminal"
        if reward is None:
            status = "terminal-no-reward"
        elif exception is not None:
            status = "terminal-with-exception"
        agent_result = result.get("agent_result") or {}
        record.update(
            {
                "status": status,
                "reward": reward,
                "exception": exception,
                "started_at": result.get("started_at"),
                "finished_at": result.get("finished_at"),
                "elapsed_seconds": iso_duration_seconds(
                    result.get("started_at"), result.get("finished_at")
                ),
                "agent_input_tokens": agent_result.get("n_input_tokens"),
                "agent_cached_tokens": agent_result.get("n_cache_tokens"),
                "agent_output_tokens": agent_result.get("n_output_tokens"),
                "agent_cost_usd": agent_result.get("cost_usd"),
            }
        )
    if not trajectory_path.is_file():
        record["exclusion_reason"] = "no agent trajectory was produced"
    elif result is None:
        record["exclusion_reason"] = "coordinator stopped before a terminal result"
    elif result.get("exception_info") is not None:
        record["exclusion_reason"] = "Harbor recorded an infrastructure or actor exception"
    elif record["reward"] not in (0, 0.0, 1, 1.0):
        record["exclusion_reason"] = "no binary reward was produced"
    else:
        record["included_in_submission"] = True
    return record


def build_trajectory_bundle(stage: Path) -> list[dict]:
    jobs_root = ROOT / "jobs"
    records: list[dict] = []
    for job_dir in sorted(path for path in jobs_root.iterdir() if path.is_dir()):
        trial_dirs = sorted(
            path
            for path in job_dir.iterdir()
            if path.is_dir() and (path / "config.json").is_file()
        )
        if not trial_dirs:
            continue
        if not any(
            json.loads((trial / "config.json").read_text())
            .get("agent", {})
            .get("model_name")
            == "gpt-5.6-luna"
            for trial in trial_dirs
        ):
            continue
        for trial_dir in trial_dirs:
            record = sanitized_record(job_dir.name, trial_dir)
            records.append(record)
            if not record["included_in_submission"]:
                continue
            destination = (
                stage
                / "trajectories/luna"
                / record["cohort"]
                / job_dir.name
                / trial_dir.name
            )
            destination.mkdir(parents=True, exist_ok=True)
            shutil.copy2(trial_dir / "agent/trajectory.json", destination / "trajectory.json")
            (destination / "record.json").write_text(
                json.dumps(record, indent=2, sort_keys=True) + "\n"
            )

    if len(records) != 47:
        raise ValueError(f"expected 47 Luna trial slots, found {len(records)}")
    if sum(bool(record["trajectory_present"]) for record in records) != 46:
        raise ValueError("expected 46 retained Luna trajectories")
    if sum(bool(record["terminal_result_present"]) for record in records) != 45:
        raise ValueError("expected 45 terminal Luna result records")
    if sum(bool(record["included_in_submission"]) for record in records) != 42:
        raise ValueError("expected 42 completed, exception-free Luna trajectories")
    return records


def write_trajectory_index(stage: Path, records: list[dict]) -> None:
    trajectory_root = stage / "trajectories"
    trajectory_root.mkdir(parents=True, exist_ok=True)
    columns = [
        "cohort",
        "job",
        "trial",
        "task",
        "model",
        "reasoning",
        "status",
        "reward",
        "elapsed_seconds",
        "trajectory_present",
        "terminal_result_present",
        "included_in_submission",
        "exclusion_reason",
    ]
    with (trajectory_root / "luna-trial-index.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

    source_guide = ROOT / "submission/private/GUIDED_TRAJECTORIES.md"
    guide = source_guide.read_text() if source_guide.is_file() else "# Agent trajectories\n"
    header = """# Agent trajectories

This folder contains the 42 completed, exception-free `gpt-5.6-luna` trajectories from the build. `luna-trial-index.csv` accounts for all 47 launched trial slots: 46 produced agent activity, 45 produced terminal Harbor results, and 42 ended with a binary reward and no exception.

Four trajectory files are deliberately omitted: two cancelled start-timestamp runs, one UDS run stranded before grading, and one PromQL run that earned reward `1` but ended with an actor-timeout exception. A fifth slot stopped before writing a trajectory. The index keeps these exclusions visible without presenting infrastructure failures as benchmark outcomes.

Each included trajectory sits under `luna/<cohort>/<job>/<trial>/` beside a compact `record.json` with its task, reward, timing, model, reasoning setting, and token totals. The five agent instructions are stored once under `task_support/prometheus/tasks/*/instruction.md` instead of being duplicated for every run.

The four cohort labels mean:

- `initial-max-calibration`: the first complete set of two attempts per task, which passed 8/10.
- `intermediate-high-calibration`: two attempts per task before the last conformance changes, which passed 7/10.
- `final-high-calibration`: two completed attempts per task on the released checks, which passed 2/10.
- `development-calibration`: other completed task-specific runs used while the episodes changed.

Raw Harbor jobs are not included. They add build logs, verifier internals, collected repository archives, sandbox state, and coordinator files to the same agent-facing record. Those local jobs occupy about 1.8 GB and are not needed to follow what the agent did.

## Guided examples

"""
    if guide.startswith("# Guided trajectories"):
        guide = guide.split("## Early start timestamp R1 - Luna max", 1)
        if len(guide) == 2:
            guide = "## Early start timestamp R1 - Luna max" + guide[1]
        else:
            guide = ""
    (trajectory_root / "README.md").write_text(header + guide)


def copy_controls(stage: Path) -> None:
    controls = ROOT / "submission/private/controls"
    if not controls.is_dir():
        return
    destination_root = stage / "trajectories/controls"
    for source in controls.rglob("*"):
        if not source.is_file():
            continue
        destination = destination_root / source.relative_to(controls)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.name != "result.json":
            shutil.copy2(source, destination)
            continue
        result = json.loads(source.read_text())
        clean = {
            "task_name": result.get("task_name"),
            "trial_name": result.get("trial_name"),
            "agent_info": result.get("agent_info"),
            "started_at": result.get("started_at"),
            "finished_at": result.get("finished_at"),
            "agent_execution": result.get("agent_execution"),
            "verifier": result.get("verifier"),
            "verifier_result": result.get("verifier_result"),
            "exception_info": result.get("exception_info"),
            "task_checksum": result.get("task_checksum"),
        }
        destination.write_text(json.dumps(clean, indent=2, sort_keys=True) + "\n")


def make_archive(stage: Path) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT.with_suffix(".zip.tmp")
    if temporary.exists():
        temporary.unlink()
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(stage.rglob("*")):
            if path.is_file():
                arcname = Path(ARCHIVE_ROOT) / path.relative_to(stage)
                info = zipfile.ZipInfo(arcname.as_posix(), date_time=(2026, 8, 31, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (path.stat().st_mode & 0xFFFF) << 16
                archive.writestr(info, path.read_bytes(), compresslevel=9)
    temporary.replace(OUTPUT)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="micro1-submission-") as temporary:
        stage = Path(temporary)
        for source in selected_source_files():
            destination = stage / source.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        records = build_trajectory_bundle(stage)
        write_trajectory_index(stage, records)
        copy_controls(stage)
        make_archive(stage)
    print(OUTPUT)
    print(f"bytes={OUTPUT.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
