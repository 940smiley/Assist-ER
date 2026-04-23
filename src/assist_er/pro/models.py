from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AuthMode(str, Enum):
    github_app = "github_app"
    oauth_device = "oauth_device"
    pat = "pat"
    fine_grained_pat = "fine_grained_pat"


class RepoRef(BaseModel):
    owner: str
    name: str
    default_branch: str = "main"

    @property
    def slug(self) -> str:
        return f"{self.owner}/{self.name}"


class RepoTriageResult(BaseModel):
    repo: str
    open_issues: int
    open_prs: int
    severity_score: int
    findings: list[str] = Field(default_factory=list)


class PullRequestState(str, Enum):
    open = "open"
    closed = "closed"
    merged = "merged"


class PullRequestRecord(BaseModel):
    number: int
    title: str
    state: PullRequestState
    draft: bool = False
    mergeable: bool | None = None
    mergeable_state: str | None = None
    labels: list[str] = Field(default_factory=list)


class BranchActionResult(BaseModel):
    success: bool
    branch: str
    action: str
    message: str


class WorkflowAuditResult(BaseModel):
    repo: str
    has_ci: bool
    has_dependabot: bool
    missing_permissions: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class DependencyUpdateResult(BaseModel):
    repo: str
    updated_files: list[str] = Field(default_factory=list)
    created_branch: str
    success: bool


class PagesResult(BaseModel):
    repo: str
    action: str
    success: bool
    details: dict[str, Any] = Field(default_factory=dict)


class AIChangeSet(BaseModel):
    summary: str
    file_updates: dict[str, str] = Field(default_factory=dict)


class PRSummary(BaseModel):
    repo: str
    number: int
    summary: str
    risks: list[str] = Field(default_factory=list)


class PrepareResult(BaseModel):
    repo: str
    triage: RepoTriageResult
    workflow_audit: WorkflowAuditResult
    dependency_update: DependencyUpdateResult
    notes: list[str] = Field(default_factory=list)
