from assist_er.models import WorkflowRequest
from assist_er.workflow_generator import WorkflowGenerator


def test_workflow_generator_includes_automerge_job() -> None:
    artifact = WorkflowGenerator().generate(WorkflowRequest(auto_merge_dependabot=True))
    assert artifact.path == ".github/workflows/assist-er.yml"
    assert "auto-merge-dependabot" in artifact.content


def test_workflow_generator_can_disable_tests() -> None:
    artifact = WorkflowGenerator().generate(WorkflowRequest(run_tests=False))
    assert "Tests" not in artifact.content
