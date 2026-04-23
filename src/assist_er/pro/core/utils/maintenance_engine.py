from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

from assist_er.pro.core.utils.event_logger import EventLogger
from assist_er.pro.core.utils.reporting import write_summary
from assist_er.pro.models import RepoRef

if TYPE_CHECKING:
    from assist_er.pro.service import ProService


class AutonomousMaintenanceEngine:
    def __init__(self, service: ProService, log_path: Path | None = None) -> None:
        self.service = service
        self.logger = EventLogger(log_path or Path(".assist-er/pro/logs/live.ndjson"))

    def run_all(self) -> dict[str, Any]:
        repos = self.service.repos.list_accessible_repositories()
        return self._run_repos(repos)

    def run_selected(self, repos: list[RepoRef]) -> dict[str, Any]:
        return self._run_repos(repos)

    def _run_repos(self, repos: list[RepoRef]) -> dict[str, Any]:
        now = datetime.now(UTC)
        summary: dict[str, Any] = {
            "started_at": now.isoformat(),
            "repos_processed": 0,
            "repos": [],
            "log_file": str(self.logger.path),
        }

        for repo in repos:
            repo_result: dict[str, Any] = {"repo": repo.slug, "actions": []}
            self.logger.log("repo_scan_start", repo=repo.slug)

            triage = self.service.triage.triage(repo)
            repo_result["triage"] = triage.model_dump()
            repo_result["actions"].append("triage")
            self.logger.log("triage_complete", repo=repo.slug, severity=triage.severity_score)

            prs = self.service.prs.list_prs(repo)
            merged = 0
            closed = 0
            for pr in prs:
                result = self.service.prs.resolve_check_merge(repo, pr.number)
                if bool(result.get("merged")):
                    merged += 1
                if not bool(result.get("merged")) and "Cannot" in str(result.get("message", "")):
                    self.service.prs.close_pr(repo, pr.number)
                    closed += 1
            repo_result["actions"].append("pr_fix_merge")
            repo_result["merged_prs"] = merged
            repo_result["closed_prs"] = closed
            self.logger.log("prs_processed", repo=repo.slug, merged=merged, closed=closed)

            cutoff = now - timedelta(days=30)
            # deterministic branch-cleaning policy for assist-er temp branches
            if not prs:
                for branch in ["assist-er/automated-edits", "assist-er/seed-example"]:
                    try:
                        self.service.branches.delete_branch(repo, branch)
                        self.logger.log("branch_deleted", repo=repo.slug, branch=branch)
                    except Exception:
                        self.logger.log("branch_delete_skipped", repo=repo.slug, branch=branch)
            repo_result["actions"].append("branch_cleanup")
            repo_result["stale_cutoff"] = cutoff.isoformat()

            dep = self.service.deps.ensure_config(repo)
            repo_result["dependency_update"] = dep.model_dump()
            repo_result["actions"].append("dependency_update")

            audit = self.service.workflows.audit(repo)
            if not audit.has_ci:
                self.service.workflows.apply_template(repo)
            repo_result["workflow_audit"] = audit.model_dump()
            repo_result["actions"].append("workflow_repair")

            ai_patch = self.service.ai_codegen.generate_tests(repo.name)
            repo_result["ai_changes"] = ai_patch.model_dump()
            repo_result["actions"].append("ai_improvements")

            self.logger.log("repo_scan_complete", repo=repo.slug, actions=repo_result["actions"])
            summary["repos"].append(repo_result)
            summary["repos_processed"] += 1

        summary["finished_at"] = datetime.now(UTC).isoformat()
        write_summary(Path(".assist-er/pro/reports/latest-summary.json"), summary)
        return summary
