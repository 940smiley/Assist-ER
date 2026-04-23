from __future__ import annotations

from assist_er.github_client import GitHubClient
from assist_er.local_repo import LocalRepositoryService
from assist_er.models import BatchEditRequest, OperationResult, RepositoryAccess, WorkflowRequest
from assist_er.triage import TriageService
from assist_er.workflow_generator import WorkflowGenerator


class AutomationService:
    def __init__(
        self,
        github: GitHubClient,
        triage_service: TriageService | None = None,
        workflow_generator: WorkflowGenerator | None = None,
        local_repo_service: LocalRepositoryService | None = None,
    ) -> None:
        self.github = github
        self.triage_service = triage_service or TriageService()
        self.workflow_generator = workflow_generator or WorkflowGenerator()
        self.local_repo_service = local_repo_service or LocalRepositoryService()

    def triage_open_issues(self, repo: RepositoryAccess) -> list[OperationResult]:
        results: list[OperationResult] = []
        for issue in self.github.list_open_issues(repo):
            decision = self.triage_service.classify(issue)
            self.github.add_labels(repo, issue.number, decision.suggested_labels)
            results.append(
                OperationResult(
                    success=True,
                    message=f"Issue #{issue.number} triaged as {decision.severity.value}",
                    details={"labels": decision.suggested_labels, "rationale": decision.rationale},
                )
            )
        return results

    def process_open_prs(self, repo: RepositoryAccess) -> list[OperationResult]:
        results: list[OperationResult] = []
        for pr in self.github.list_open_pull_requests(repo):
            if pr.draft:
                results.append(
                    OperationResult(
                        success=True,
                        message=f"Skipped draft PR #{pr.number}",
                    )
                )
                continue
            mergeable = pr.mergeable_state in {None, "clean", "has_hooks", "unstable"}
            if not mergeable:
                results.append(
                    OperationResult(
                        success=False,
                        message=f"PR #{pr.number} requires manual intervention",
                        details={"mergeable_state": pr.mergeable_state},
                    )
                )
                continue
            self.github.merge_pull_request(repo, pr.number)
            results.append(OperationResult(success=True, message=f"Merged PR #{pr.number}"))
        return results

    def generate_workflow(self, request: WorkflowRequest) -> OperationResult:
        artifact = self.workflow_generator.generate(request)
        return OperationResult(
            success=True,
            message="Workflow generated",
            details=artifact.model_dump(),
        )

    def apply_batch_edits(self, request: BatchEditRequest) -> OperationResult:
        return self.local_repo_service.apply_batch_edits(request)
