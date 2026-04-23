from typer.testing import CliRunner

from assist_er.cli import app


def test_budget_flag_parses() -> None:
    result = CliRunner().invoke(app, ["--budget", "--help"])
    assert result.exit_code == 0
