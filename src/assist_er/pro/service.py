from __future__ import annotations

from pathlib import Path

from assist_er.config import settings
from assist_er.pro.core.ai.codegen import CodeGenerator
from assist_er.pro.core.ai.reviewer import PRReviewer
from assist_er.pro.core.api.graphql import GraphQLClient
from assist_er.pro.core.api.rest import RestClient
from assist_er.pro.core.auth.manager import AuthContext, AuthManager
from assist_er.pro.core.auth.token_store import EncryptedTokenStore
from assist_er.pro.core.repos.branch_manager import BranchManager
from assist_er.pro.core.repos.pr_manager import PullRequestManager
from assist_er.pro.core.repos.repository_manager import RepositoryManager
from assist_er.pro.core.repos.triage_engine import RepoTriageEngine
from assist_er.pro.core.repos.workflow_manager import WorkflowManager
from assist_er.pro.core.utils.maintenance_engine import AutonomousMaintenanceEngine
from assist_er.pro.plugins.custom_automation import CustomAutomation
from assist_er.pro.plugins.dependabot_helper import DependabotHelper
from assist_er.pro.plugins.pages_helper import PagesHelper


class ProService:
    def __init__(self, auth: AuthContext | None = None, require_token: bool = True) -> None:
        self.auth_manager = AuthManager(settings.github_api_url)
        self.token_store = EncryptedTokenStore(
            key_path=Path(settings.pro_token_key_path),
            token_path=Path(settings.pro_token_store_path),
        )
        if auth is None:
            token = settings.github_token or self.token_store.load("default")
            if not token and require_token:
                raise RuntimeError("No token available. Set GITHUB_TOKEN or run pro auth login.")
            auth = self.auth_manager.from_pat(token or "")

        self.rest = RestClient(token=auth.token, base_url=settings.github_api_url)
        self.graphql = GraphQLClient(self.rest)
        self.repos = RepositoryManager(self.rest)
        self.triage = RepoTriageEngine(self.rest)
        self.prs = PullRequestManager(self.rest)
        self.branches = BranchManager(self.rest)
        self.workflows = WorkflowManager(self.rest)
        self.deps = DependabotHelper(self.rest)
        self.pages = PagesHelper(self.rest)
        self.automation = CustomAutomation(self.triage, self.workflows, self.deps, self.prs)
        self.maintenance = AutonomousMaintenanceEngine(self)
        self.ai_codegen = CodeGenerator()
        self.ai_reviewer = PRReviewer()

    def close(self) -> None:
        self.rest.close()
