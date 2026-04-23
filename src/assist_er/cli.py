from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from assist_er.github_client import GitHubClient
from assist_er.logging_utils import configure_logging
from assist_er.models import BatchEditRequest, RepositoryAccess, WorkflowRequest
from assist_er.pro.core.utils.gui_bridge import launch_gui
from assist_er.pro.models import RepoRef
from assist_er.pro.service import ProService
from assist_er.services import AutomationService

app = typer.Typer(help="Assist-ER automation CLI")
repos_app = typer.Typer(help="Repository operations")
prs_app = typer.Typer(help="Pull request operations")
ai_app = typer.Typer(help="AI operations")
auth_app = typer.Typer(help="Authentication operations (pro mode)")
app.add_typer(repos_app, name="repos")
repos_app.add_typer(prs_app, name="prs")
app.add_typer(ai_app, name="ai")
app.add_typer(auth_app, name="auth")

console = Console()


class ModeState:
    pro_mode: bool = False


state = ModeState()


def _budget_service() -> AutomationService:
    configure_logging()
    return AutomationService(github=GitHubClient())


def _pro_service() -> ProService:
    configure_logging()
    return ProService()


def _pro_auth_service() -> ProService:
    configure_logging()
    return ProService(require_token=False)


def _get_repo_ref(service: ProService, owner: str, repo: str) -> RepoRef:
    selected = service.repos.select_repositories([f"{owner}/{repo}"])
    if not selected:
        raise typer.BadParameter(f"Repository not accessible: {owner}/{repo}")
    return selected[0]


@app.callback()
def main(
    pro: bool = typer.Option(False, "--pro", help="Run assist-er pro architecture"),
    budget: bool = typer.Option(False, "--budget", help="Run lightweight budget architecture"),
) -> None:
    if pro and budget:
        raise typer.BadParameter("Use only one mode flag: --pro or --budget")
    state.pro_mode = pro and not budget


@app.command("work")
def work() -> None:
    """Run autonomous repo maintenance across all accessible repositories (pro mode)."""
    service = _pro_service()
    summary = service.maintenance.run_all()
    console.print_json(json.dumps(summary))


# Backward-compatible budget commands.
@app.command("triage")
def triage(owner: str, repo: str) -> None:
    results = _budget_service().triage_open_issues(RepositoryAccess(owner=owner, name=repo))
    console.print_json(json.dumps([r.model_dump() for r in results]))


@app.command("prs")
def process_prs(owner: str, repo: str) -> None:
    results = _budget_service().process_open_prs(RepositoryAccess(owner=owner, name=repo))
    console.print_json(json.dumps([r.model_dump() for r in results]))


@app.command("generate-workflow")
def generate_workflow(name: str = "assist-er-maintenance") -> None:
    artifact = _budget_service().generate_workflow(WorkflowRequest(name=name))
    console.print_json(json.dumps(artifact.model_dump()))


@app.command("batch-edit")
def batch_edit(owner: str, repo: str, path: str, content: str) -> None:
    request = BatchEditRequest(
        repository=RepositoryAccess(owner=owner, name=repo),
        file_updates={path: content},
    )
    result = _budget_service().apply_batch_edits(request)
    console.print_json(json.dumps(result.model_dump()))


@repos_app.callback(invoke_without_command=True)
def repos_root(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand:
        return
    if state.pro_mode:
        gui_path = launch_gui()
        console.print(f"Assist-ER Pro GUI launched: {gui_path}")
        return

    with GitHubClient() as github:
        budget_repos = github.list_user_repositories()
    for repo in budget_repos:
        console.print(f"- {repo.slug}")


@repos_app.command("triage")
def repos_triage(owner: str, repo: str) -> None:
    if not state.pro_mode:
        triage(owner, repo)
        return
    service = _pro_service()
    repo_ref = _get_repo_ref(service, owner, repo)
    result = service.triage.triage(repo_ref)
    console.print_json(result.model_dump_json())


@repos_app.command("prepare")
def repos_prepare(owner: str, repo: str) -> None:
    service = _pro_service()
    repo_ref = _get_repo_ref(service, owner, repo)
    result = service.automation.prepare(repo_ref)
    console.print_json(result.model_dump_json())


@repos_app.command("deps")
def repos_deps(owner: str, repo: str) -> None:
    service = _pro_service()
    repo_ref = _get_repo_ref(service, owner, repo)
    result = service.deps.ensure_config(repo_ref)
    console.print_json(result.model_dump_json())


@repos_app.command("pages")
def repos_pages(owner: str, repo: str, repair: bool = False) -> None:
    service = _pro_service()
    repo_ref = _get_repo_ref(service, owner, repo)
    result = service.pages.repair_pages(repo_ref) if repair else service.pages.setup_pages(repo_ref)
    console.print_json(result.model_dump_json())


@repos_app.command("workflows")
def repos_workflows(owner: str, repo: str, fix: bool = False) -> None:
    service = _pro_service()
    repo_ref = _get_repo_ref(service, owner, repo)
    if fix:
        apply_result = service.workflows.apply_template(repo_ref)
        console.print_json(json.dumps(apply_result))
        return
    audit_result = service.workflows.audit(repo_ref)
    console.print_json(audit_result.model_dump_json())


@repos_app.command("branch-create")
def repos_branch_create(owner: str, repo: str, branch: str, from_branch: str = "") -> None:
    service = _pro_service()
    repo_ref = _get_repo_ref(service, owner, repo)
    source = from_branch or None
    result = service.branches.create_branch(repo_ref, branch, source)
    console.print_json(result.model_dump_json())


@repos_app.command("branch-delete")
def repos_branch_delete(owner: str, repo: str, branch: str) -> None:
    service = _pro_service()
    repo_ref = _get_repo_ref(service, owner, repo)
    result = service.branches.delete_branch(repo_ref, branch)
    console.print_json(result.model_dump_json())


@repos_app.command("monitor")
def repos_monitor(owner: str, repo: str, cycles: int = 1) -> None:
    service = _pro_service()
    repo_ref = _get_repo_ref(service, owner, repo)
    logs: list[dict[str, object]] = []
    for index in range(cycles):
        triage_result = service.triage.triage(repo_ref)
        merged: list[dict[str, str | bool]] = []
        for pr in service.prs.list_prs(repo_ref):
            if pr.draft:
                continue
            merged.append(service.prs.resolve_check_merge(repo_ref, pr.number))
        logs.append(
            {
                "cycle": index + 1,
                "triage": triage_result.model_dump(),
                "pr_actions": merged,
            }
        )
    console.print_json(json.dumps(logs))


@prs_app.callback(invoke_without_command=True)
def prs_root(ctx: typer.Context, owner: str = "", repo: str = "") -> None:
    if ctx.invoked_subcommand:
        return
    if state.pro_mode:
        service = _pro_service()
        repo_ref = _get_repo_ref(service, owner, repo)
        prs = service.prs.list_prs(repo_ref)
        console.print_json(json.dumps([pr.model_dump() for pr in prs]))
        return
    process_prs(owner, repo)


@prs_app.command("merge")
def prs_merge(owner: str, repo: str, number: int) -> None:
    service = _pro_service()
    repo_ref = _get_repo_ref(service, owner, repo)
    result = service.prs.merge_pr(repo_ref, number)
    console.print_json(json.dumps(result))


@prs_app.command("resolve")
def prs_resolve(owner: str, repo: str, number: int, check: bool = True, merge: bool = True) -> None:
    service = _pro_service()
    repo_ref = _get_repo_ref(service, owner, repo)
    if check and merge:
        result = service.prs.resolve_check_merge(repo_ref, number)
        console.print_json(json.dumps(result))


@app.command("prepare")
def prepare(owner: str, repo: str) -> None:
    repos_prepare(owner, repo)


@ai_app.command("improve")
def ai_improve(path: str) -> None:
    service = _pro_service()
    content = Path(path).read_text(encoding="utf-8")
    result = service.ai_codegen.improve_file(path, content)
    console.print_json(result.model_dump_json())


@ai_app.command("tests")
def ai_tests(module: str) -> None:
    service = _pro_service()
    result = service.ai_codegen.generate_tests(module)
    console.print_json(result.model_dump_json())


@ai_app.command("pr-summary")
def ai_pr_summary(repo: str, number: int, title: str, body: str = "") -> None:
    service = _pro_service()
    result = service.ai_reviewer.summarize(repo, number, title, body)
    console.print_json(result.model_dump_json())


@auth_app.command("login-pat")
def auth_login_pat(token: str, fine_grained: bool = False, alias: str = "default") -> None:
    service = _pro_auth_service()
    context = service.auth_manager.from_pat(token=token, fine_grained=fine_grained)
    service.token_store.save(alias, context.token)
    console.print(f"Saved token alias '{alias}' in encrypted store.")


@auth_app.command("login-app")
def auth_login_app(
    app_id: str,
    installation_id: str,
    private_key_pem: str,
    alias: str = "default",
) -> None:
    service = _pro_auth_service()
    context = service.auth_manager.from_github_app_installation(
        app_id,
        installation_id,
        private_key_pem,
    )
    service.token_store.save(alias, context.token)
    console.print(f"Saved GitHub App installation token alias '{alias}'.")


@auth_app.command("device-start")
def auth_device_start(client_id: str, scope: str = "repo") -> None:
    service = _pro_auth_service()
    payload = service.auth_manager.start_device_flow(client_id, scope)
    console.print_json(json.dumps(payload))


if __name__ == "__main__":
    app()
