from __future__ import annotations

import logging
import subprocess
from pathlib import Path

from assist_er.config import settings
from assist_er.models import BatchEditRequest, OperationResult

logger = logging.getLogger(__name__)


class LocalRepositoryService:
    def __init__(self, workspace_dir: Path | None = None) -> None:
        self.workspace_dir = workspace_dir or settings.workspace_dir
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

    def _run(self, args: list[str], cwd: Path | None = None) -> None:
        logger.debug("Running command: %s", " ".join(args))
        subprocess.run(args, cwd=cwd, check=True, text=True, capture_output=True)

    def clone_if_needed(self, slug: str) -> Path:
        repo_dir = self.workspace_dir / slug.replace("/", "__")
        if repo_dir.exists():
            self._run(["git", "fetch", "origin"], cwd=repo_dir)
            self._run(["git", "checkout", "main"], cwd=repo_dir)
            self._run(["git", "pull", "origin", "main"], cwd=repo_dir)
            return repo_dir

        clone_url = f"https://github.com/{slug}.git"
        self._run(["git", "clone", clone_url, str(repo_dir)])
        return repo_dir

    def apply_batch_edits(self, request: BatchEditRequest) -> OperationResult:
        try:
            repo_dir = self.clone_if_needed(request.repository.slug)
            self._run(["git", "checkout", "-B", request.branch_name], cwd=repo_dir)
            for rel_path, content in request.file_updates.items():
                target = repo_dir / rel_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
            self._run(["git", "add", "."], cwd=repo_dir)
            self._run(["git", "commit", "-m", "assist-er: automated batch edits"], cwd=repo_dir)
            self._run(["git", "push", "-u", "origin", request.branch_name], cwd=repo_dir)
            return OperationResult(
                success=True,
                message="Batch edits applied.",
                details={"path": str(repo_dir)},
            )
        except subprocess.CalledProcessError as exc:
            return OperationResult(
                success=False,
                message="Failed to apply batch edits.",
                details={"stderr": exc.stderr, "stdout": exc.stdout},
            )
