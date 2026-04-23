from __future__ import annotations

import json

import typer
from rich.console import Console

from assist_er.github_client import GitHubClient
from assist_er.logging_utils import configure_logging
from assist_er.models import BatchEditRequest, RepositoryAccess, WorkflowRequest
from assist_er.services import AutomationService

app = typer.Typer(help="Assist-ER automation CLI")
console = Console()


def _service() -> AutomationService:
    configure_logging()
    return AutomationService(github=GitHubClient())


@app.command("repos")
def list_repositories() -> None:
    with GitHubClient() as github:
        repos = github.list_user_repositories()
    for repo in repos:
        console.print(f"- {repo.slug}")


@app.command("triage")
def triage(owner: str, repo: str) -> None:
    results = _service().triage_open_issues(RepositoryAccess(owner=owner, name=repo))
    console.print_json(json.dumps([r.model_dump() for r in results]))


@app.command("prs")
def process_prs(owner: str, repo: str) -> None:
    results = _service().process_open_prs(RepositoryAccess(owner=owner, name=repo))
    console.print_json(json.dumps([r.model_dump() for r in results]))


@app.command("generate-workflow")
def generate_workflow(name: str = "assist-er-maintenance") -> None:
    artifact = _service().generate_workflow(WorkflowRequest(name=name))
    console.print_json(json.dumps(artifact.model_dump()))


@app.command("batch-edit")
def batch_edit(owner: str, repo: str, path: str, content: str) -> None:
    request = BatchEditRequest(
        repository=RepositoryAccess(owner=owner, name=repo),
        file_updates={path: content},
    )
    result = _service().apply_batch_edits(request)
    console.print_json(json.dumps(result.model_dump()))


if __name__ == "__main__":
    app()
