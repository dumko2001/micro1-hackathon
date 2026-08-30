"""Run one reviewer-owned candidate fixture inside a Harbor task environment."""

from __future__ import annotations

from pathlib import Path
import re

from harbor.agents.base import BaseAgent
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext


PACKAGE_TO_LOGICAL = {
    "unix-socket-scraping": "unix-socket-scraping",
    "prometheus-subquery-semantics": "step-invariant-subquery",
    "histogram-rate-semantics": "native-histogram-rate",
    "start-timestamp-persistence": "start-timestamp-persistence",
    "stale-wal-expiry": "stale-series-wal-expiry",
}


class CandidateFixtureAgent(BaseAgent):
    """Upload and execute a private calibration fixture selected by task name."""

    @staticmethod
    def name() -> str:
        return "candidate-fixture"

    def __init__(
        self,
        logs_dir: Path,
        candidate_id: str,
        fixture_root: str = ".private-eval/candidates",
        model_name: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(logs_dir=logs_dir, model_name=model_name, **kwargs)
        if re.fullmatch(r"[a-z0-9][a-z0-9-]*", candidate_id) is None:
            raise ValueError(f"unsafe candidate id: {candidate_id!r}")
        self._candidate_id = candidate_id
        self._fixture_root = Path(fixture_root).resolve()

    def version(self) -> str:
        return "1.0.0"

    async def setup(self, environment: BaseEnvironment) -> None:
        return

    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        package = environment.environment_name
        logical = PACKAGE_TO_LOGICAL.get(package)
        if logical is None:
            raise ValueError(f"unsupported Harbor task package: {package}")
        fixture_dir = self._fixture_root / logical / self._candidate_id
        fixture_patch = self._fixture_root / logical / f"{self._candidate_id}.patch"
        remote = "/tmp/micro1-candidate-fixture"
        if (fixture_dir / "solve.sh").is_file():
            await environment.upload_dir(source_dir=fixture_dir, target_dir=remote)
            workspace_root = self._fixture_root.parents[1]
            solution_dir = workspace_root / "tasks" / package / "solution"
            if solution_dir.is_dir():
                await environment.upload_dir(
                    source_dir=solution_dir,
                    target_dir="/tmp/micro1-reference-solution",
                )
            await environment.exec(command=f"chmod 0555 {remote}/solve.sh", user="root")
            command = (
                "MICRO1_REFERENCE_SOLUTION=/tmp/micro1-reference-solution "
                f"{remote}/solve.sh"
            )
        elif fixture_patch.is_file():
            remote_patch = f"{remote}.patch"
            await environment.upload_file(
                source_path=fixture_patch,
                target_path=remote_patch,
            )
            command = f"cd /app/prometheus && git apply {remote_patch}"
        else:
            raise FileNotFoundError(
                f"missing calibration fixture: {fixture_dir} or {fixture_patch}"
            )

        result = await environment.exec(command=command, timeout_sec=3600)
        (self.logs_dir / "candidate-fixture.txt").write_text(
            f"task={logical}\ncandidate={self._candidate_id}\nexit_code={result.return_code}\n"
        )
        if result.return_code != 0:
            raise RuntimeError(
                f"candidate fixture {logical}/{self._candidate_id} exited "
                f"with {result.return_code}"
            )

