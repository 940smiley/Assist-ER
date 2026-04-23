# Assist-ER

Assist-ER provides two operation profiles in one codebase:

- **Budget mode** (`assist-er --budget`): lightweight CLI automation (backward-compatible existing behavior).
- **Pro mode** (`assist-er --pro`): advanced automation, GUI control center, autonomous maintenance engine, and Windows packaging support.

## Mode Switch

- `assist-er --budget ...` keeps minimal legacy behavior.
- `assist-er --pro ...` enables advanced architecture and GUI workflows.

## Budget Mode (unchanged)

```bash
assist-er repos
assist-er triage <owner> <repo>
assist-er prs <owner> <repo>
assist-er generate-workflow
assist-er batch-edit <owner> <repo> <path> <content>
```

## Pro Mode CLI

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
assist-er --pro repos branch-create <owner> <repo> <branch>
assist-er --pro repos branch-delete <owner> <repo> <branch>
assist-er --pro repos monitor <owner> <repo> --cycles 3
assist-er --pro auth login-pat <token>
assist-er --pro auth login-app <app_id> <installation_id> <private_key_pem>
assist-er --pro auth device-start <client_id>
assist-er --pro ai improve <path>
assist-er --pro ai tests <module>
assist-er --pro ai pr-summary <repo> <number> <title> [body]
assist-er --pro prepare <owner> <repo>
assist-er --pro work
```

## `assist-er work` (Autonomous maintenance)

`assist-er --pro work` runs a full maintenance cycle across all accessible repos:

1. List repos.
2. Scan and triage each repo.
3. Attempt PR resolution/merge; close non-safe stale PRs.
4. Clean automation branches.
5. Update dependencies (Dependabot config).
6. Audit/fix workflows and generate missing template workflows.
7. Run AI-assisted improvements/test scaffolding metadata.
8. Write summary report to `.assist-er/pro/reports/latest-summary.json`.
9. Stream event logs to `.assist-er/pro/logs/live.ndjson` for GUI viewing.

## Pro Architecture

```text
src/assist_er/pro/
  core/
    auth/        # GitHub App/PAT/device-flow + encrypted token store
    api/         # REST + GraphQL + pagination
    repos/       # repo list + triage + PR + branch + workflow managers
    prs/         # PR interface exports
    branches/    # branch interface exports
    workflows/   # workflow interface exports
    ai/          # codegen/conflict-review helpers
    utils/       # event logger, reporting, autonomous engine, GUI bridge
  plugins/       # dependabot helper, pages helper, custom automation
  templates/     # workflow/dependabot/pages templates
  schemas/       # output JSON schemas
  service.py
```

## GUI (`gui/`)

The Pro GUI is a NeutralinoJS desktop app with screens/panels for:

- Authentication
- Repo browsing
- PR dashboard
- Workflow dashboard
- Settings
- Logs panel

Buttons are wired to trigger pro maintenance commands and refresh live logs.

### Run GUI

```bash
npm i -g @neutralinojs/neu
cd gui
neu run
```

## Windows EXE + MSIX Packaging (`build/`)

- `build/build_windows.ps1` builds GUI release artifacts and prepares MSIX metadata.
- `build/msix/AppxManifest.xml` includes package identity and executable metadata with a text icon placeholder.
- `build/auto-update.json` contains update-channel metadata.
- Signing step is provided as a release-pipeline placeholder in `build/msix/README.md`.

## GitHub Pages Demo (`pages/`)

- Demo website source: `pages/site/`
- Deployment workflow for `pages` branch: `pages/site/.github/workflows/pages.yml`
- Includes landing page, dark theme, features, examples, install notes, architecture summary.

## API Endpoints

Budget endpoints remain:

- `GET /health`
- `POST /repos/{owner}/{repo}/triage`
- `POST /repos/{owner}/{repo}/prs/process`
- `POST /workflow/generate`
- `POST /batch-edits`

Pro endpoints:

- `GET /pro/repos`
- `POST /pro/repos/{owner}/{repo}/prepare`

## Install & Validate

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
ruff check src tests
pytest
mypy src/assist_er
assist-er --help
assist-er --pro --help
```
