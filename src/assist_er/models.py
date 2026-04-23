from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ControlMode(str, Enum):
    full = "full"
    limited = "limited"


class RepositoryAccess(BaseModel):
    owner: str
    name: str
    enabled: bool = True
    control_mode: ControlMode = ControlMode.limited

    @property
    def slug(self) -> str:
        return f"{self.owner}/{self.name}"


class PullRequest(BaseModel):
    number: int
    title: str
    state: str
    mergeable_state: str | None = None
    draft: bool = False
    labels: list[str] = Field(default_factory=list)
    html_url: str


class Issue(BaseModel):
    number: int
    title: str
    state: str
    labels: list[str] = Field(default_factory=list)
    body: str = ""
    html_url: str


class TriageSeverity(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class TriageDecision(BaseModel):
    issue_number: int
    severity: TriageSeverity
    rationale: str
    suggested_labels: list[str]


class WorkflowRequest(BaseModel):
    name: str = "assist-er-maintenance"
    run_tests: bool = True
    run_lint: bool = True
    auto_merge_dependabot: bool = True


class WorkflowArtifact(BaseModel):
    path: str
    content: str


class BatchEditRequest(BaseModel):
    repository: RepositoryAccess
    branch_name: str = "assist-er/automated-edits"
    file_updates: dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of repository-relative file path to new file content.",
    )


class OperationResult(BaseModel):
    success: bool
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
