from __future__ import annotations

from typing import Any

import yaml

from assist_er.models import WorkflowArtifact, WorkflowRequest


class WorkflowGenerator:
    def generate(self, request: WorkflowRequest) -> WorkflowArtifact:
        workflow: dict[str, Any] = {
            "name": request.name,
            "on": {
                "pull_request": {"branches": ["main"]},
                "push": {"branches": ["main"]},
                "schedule": [{"cron": "0 */6 * * *"}],
            },
            "permissions": {
                "contents": "write",
                "pull-requests": "write",
                "issues": "write",
            },
            "jobs": {
                "quality": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"uses": "actions/checkout@v4"},
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v5",
                            "with": {"python-version": "3.11"},
                        },
                        {"name": "Install dependencies", "run": "pip install -e .[dev]"},
                    ],
                }
            },
        }

        steps: list[dict[str, Any]] = workflow["jobs"]["quality"]["steps"]
        if request.run_lint:
            steps.append({"name": "Lint", "run": "ruff check src tests"})
        if request.run_tests:
            steps.append({"name": "Tests", "run": "pytest"})
        if request.auto_merge_dependabot:
            workflow["jobs"]["auto-merge-dependabot"] = {
                "if": "github.actor == 'dependabot[bot]'",
                "runs-on": "ubuntu-latest",
                "needs": ["quality"],
                "steps": [
                    {
                        "name": "Enable auto-merge",
                        "run": (
                            "gh pr merge --auto --squash "
                            "${{ github.event.pull_request.number }}"
                        ),
                        "env": {"GH_TOKEN": "${{ secrets.GITHUB_TOKEN }}"},
                    }
                ],
            }

        return WorkflowArtifact(
            path=".github/workflows/assist-er.yml",
            content=yaml.safe_dump(workflow, sort_keys=False),
        )
