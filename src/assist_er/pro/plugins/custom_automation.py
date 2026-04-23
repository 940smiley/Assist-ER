from __future__ import annotations

from assist_er.pro.core.repos.pr_manager import PullRequestManager
from assist_er.pro.core.repos.triage_engine import RepoTriageEngine
from assist_er.pro.core.repos.workflow_manager import WorkflowManager
from assist_er.pro.models import PrepareResult, RepoRef
from assist_er.pro.plugins.dependabot_helper import DependabotHelper


class CustomAutomation:
    def __init__(
        self,
        triage_engine: RepoTriageEngine,
        workflow_manager: WorkflowManager,
        dependabot_helper: DependabotHelper,
        pr_manager: PullRequestManager,
    ) -> None:
        self.triage_engine = triage_engine
        self.workflow_manager = workflow_manager
        self.dependabot_helper = dependabot_helper
        self.pr_manager = pr_manager

    def prepare(self, repo: RepoRef) -> PrepareResult:
        triage = self.triage_engine.triage(repo)
        audit = self.workflow_manager.audit(repo)
        dep_update = self.dependabot_helper.ensure_config(repo)
        notes: list[str] = []
        if triage.open_prs > 0:
            notes.append("Open PRs detected; run 'assist-er --pro repos prs' to inspect")
        if audit.recommendations:
            notes.extend(audit.recommendations)
        return PrepareResult(
            repo=repo.slug,
            triage=triage,
            workflow_audit=audit,
            dependency_update=dep_update,
            notes=notes,
        )
