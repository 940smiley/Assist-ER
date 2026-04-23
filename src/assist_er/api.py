from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException

from assist_er.config import settings
from assist_er.github_client import GitHubAPIError, GitHubClient
from assist_er.logging_utils import configure_logging
from assist_er.models import BatchEditRequest, OperationResult, RepositoryAccess, WorkflowRequest
from assist_er.pro.service import ProService
from assist_er.services import AutomationService

app = FastAPI(title="Assist-ER API", version="2.0.0")


def get_service() -> AutomationService:
    github = GitHubClient()
    return AutomationService(github=github)


def get_pro_service() -> ProService:
    return ProService()


service_dependency = Depends(get_service)
pro_service_dependency = Depends(get_pro_service)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/repos/{owner}/{repo}/triage", response_model=list[OperationResult])
def triage_issues(
    owner: str,
    repo: str,
    service: AutomationService = service_dependency,
) -> list[OperationResult]:
    try:
        return service.triage_open_issues(RepositoryAccess(owner=owner, name=repo))
    except GitHubAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/repos/{owner}/{repo}/prs/process", response_model=list[OperationResult])
def process_prs(
    owner: str,
    repo: str,
    service: AutomationService = service_dependency,
) -> list[OperationResult]:
    try:
        return service.process_open_prs(RepositoryAccess(owner=owner, name=repo))
    except GitHubAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/workflow/generate", response_model=OperationResult)
def generate_workflow(
    request: WorkflowRequest,
    service: AutomationService = service_dependency,
) -> OperationResult:
    return service.generate_workflow(request)


@app.post("/batch-edits", response_model=OperationResult)
def batch_edits(
    request: BatchEditRequest,
    service: AutomationService = service_dependency,
) -> OperationResult:
    return service.apply_batch_edits(request)


@app.get("/pro/repos")
def pro_repos(service: ProService = pro_service_dependency) -> list[dict[str, str]]:
    return [repo.model_dump() for repo in service.repos.list_accessible_repositories()]


@app.post("/pro/repos/{owner}/{repo}/prepare")
def pro_prepare(
    owner: str,
    repo: str,
    service: ProService = pro_service_dependency,
) -> dict[str, object]:
    selected = service.repos.select_repositories([f"{owner}/{repo}"])
    if not selected:
        raise HTTPException(status_code=404, detail="Repository not accessible")
    result = service.automation.prepare(selected[0])
    return result.model_dump()


def run() -> None:
    import uvicorn

    configure_logging(settings.log_level)
    uvicorn.run("assist_er.api:app", host="0.0.0.0", port=8000, reload=False)
