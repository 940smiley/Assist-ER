# Assist-ER

Assist-ER now ships in **two fully runnable modes**:

- **Budget mode**: lightweight automation (original implementation preserved for backward compatibility).
- **Pro mode**: expanded architecture with modular auth, REST/GraphQL clients, repo operations, AI helpers, and plugins.

## Modes

### Budget mode (default)
Backward-compatible commands (unchanged behavior):

```bash
assist-er repos
assist-er triage <owner> <repo>
assist-er prs <owner> <repo>
assist-er generate-workflow
assist-er batch-edit <owner> <repo> <path> <content>
```

### Pro mode
Enable with `--pro` and use expanded command groups:

```bash
assist-er --pro repos
assist-er --pro repos triage <owner> <repo>
assist-er --pro repos prs <owner> <repo>
assist-er --pro repos prs merge <owner> <repo> <number>
assist-er --pro repos prs resolve <owner> <repo> <number> --check --merge
assist-er --pro repos workflows <owner> <repo>
assist-er --pro repos workflows <owner> <repo> --fix
assist-er --pro repos deps <owner> <repo>
assist-er --pro repos pages <owner> <repo>
assist-er --pro repos pages <owner> <repo> --repair
assist-er --pro prepare <owner> <repo>
assist-er --pro ai improve <path>
assist-er --pro ai tests <module>
assist-er --pro ai pr-summary <repo> <number> <title> [body]
```

Use `--budget` explicitly if desired:

```bash
assist-er --budget repos
```

## Architecture

```text
src/assist_er/
  (budget mode modules preserved)

src/assist_er/pro/
  core/auth/
    manager.py                 # GitHub App/PAT/device-flow auth handling
    token_store.py             # encrypted token store
  core/api/
    rest.py                    # REST client
    graphql.py                 # GraphQL client
    pagination.py              # pagination helpers
  core/repos/
    repository_manager.py      # repo listing/selection
    triage_engine.py           # repo triage engine
    pr_manager.py              # PR list/merge/close/resolve-check-merge
    branch_manager.py          # branch create/delete
    workflow_manager.py        # workflow audit/fix
  core/ai/
    codegen.py                 # deterministic code improvements + test generation
    conflict_resolver.py       # conflict handling strategy
    reviewer.py                # PR summary + risk extraction
  plugins/
    dependabot_helper.py       # dependency automation support
    pages_helper.py            # GitHub Pages setup/repair
    custom_automation.py       # full prepare pipeline orchestration
  templates/
    pro_maintenance.yml
    dependabot.yml
    pages_index.html
  schemas/
    triage.schema.json
    prepare.schema.json
  service.py
```

## API

Budget endpoints remain available:

- `GET /health`
- `POST /repos/{owner}/{repo}/triage`
- `POST /repos/{owner}/{repo}/prs/process`
- `POST /workflow/generate`
- `POST /batch-edits`

Pro endpoints added:

- `GET /pro/repos`
- `POST /pro/repos/{owner}/{repo}/prepare`

## Authentication

Supported in pro architecture:

- GitHub App installation token flow interface
- OAuth device flow initiation
- PAT support (classic and fine-grained)
- Encrypted local token storage

Set `GITHUB_TOKEN` for immediate operation, or store token in the encrypted pro token store.

## Install & Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
assist-er --help
assist-er-api
```

## Quality

```bash
ruff check src tests
pytest
mypy src/assist_er
```
