# Assist-ER

Assist-ER is a production-ready GitHub automation application for repository operations teams.
It combines API + CLI tooling to automate pull request handling, issue triage, workflow generation,
and local batch code edits across selected repositories.

## Product Vision

Assist-ER is built for engineering managers, platform teams, and maintainers who need automation
without surrendering governance.

### Core capabilities

- Connect to GitHub with a personal/app token.
- Operate on all repositories or an explicitly selected subset.
- Continuously triage issues with severity labels.
- Process open PRs (skip drafts, merge eligible PRs).
- Generate reusable GitHub Actions workflows (tests/lint/automerge).
- Clone repositories locally and apply deterministic batch edits.
- Provide API endpoints for orchestrators and a CLI for operator workflows.

## Architecture

```text
src/assist_er/
  api.py               FastAPI entrypoints
  cli.py               Typer CLI commands
  config.py            Environment-driven settings
  github_client.py     Typed GitHub HTTP client
  local_repo.py        Git clone/edit/commit/push logic
  models.py            Pydantic domain models
  services.py          Core orchestration service
  triage.py            Severity + labeling policy
  workflow_generator.py GitHub Actions generator
  logging_utils.py     Structured logging setup
```

### Design principles

- **Modular domain services** with explicit boundaries.
- **Typed models** with Pydantic validation at API and service boundaries.
- **Deterministic, testable logic** for triage and workflow generation.
- **Operational safety** via explicit control modes, structured operation results, and retry logic for API calls.

## Quick Start

### 1) Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### 2) Configure

Create `.env` in repo root:

```bash
GITHUB_TOKEN=ghp_xxx
ASSIST_ER_LOG_LEVEL=INFO
ASSIST_ER_WORKSPACE_DIR=.assist-er/workspace
```

### 3) Run API

```bash
assist-er-api
# or
uvicorn assist_er.api:app --host 0.0.0.0 --port 8000
```

### 4) Run CLI

```bash
assist-er repos
assist-er triage <owner> <repo>
assist-er prs <owner> <repo>
assist-er generate-workflow
assist-er batch-edit <owner> <repo> <path> <content>
```

## API Endpoints

- `GET /health`
- `POST /repos/{owner}/{repo}/triage`
- `POST /repos/{owner}/{repo}/prs/process`
- `POST /workflow/generate`
- `POST /batch-edits`

### Example: Generate workflow

```bash
curl -X POST http://localhost:8000/workflow/generate \
  -H "Content-Type: application/json" \
  -d '{"name":"assist-er-maintenance","run_tests":true,"run_lint":true,"auto_merge_dependabot":true}'
```

## Triage Policy

Assist-ER applies severity based on issue text:

- `critical`: outage, security, data loss, payment failure
- `high`: bug/failure language
- `medium`: quality/performance/UX degradations
- `low`: everything else

Each issue receives suggested labels to speed maintainers' triage workflow.

## Local Batch Edit Workflow

1. Clone repo into `.assist-er/workspace` if needed.
2. Create/reset automation branch.
3. Apply file content updates.
4. Commit with deterministic message.
5. Push branch for PR creation in downstream flow.

A sample payload generator is available:

```bash
python scripts/seed_example.py
```

## Quality Controls

- Linting: `ruff check src tests`
- Tests: `pytest`
- Strict typing: `mypy src/assist_er`

CI workflow lives at `.github/workflows/ci.yml`.

## Security and Governance

- Token-based auth using `GITHUB_TOKEN`.
- Default limited-control repository model with explicit `full`/`limited` mode.
- No account-level settings mutations are performed implicitly.
- All automation actions return structured status results for auditability.

## Roadmap

- GitHub App installation flow + OAuth handshake.
- PR conflict auto-resolution strategies.
- Persistent job scheduler for continuous repo scanning.
- Policy-as-code for repository-specific automation rules.
