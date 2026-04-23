from typer.testing import CliRunner

from assist_er import cli


class FakeMaintenance:
    def run_all(self) -> dict[str, object]:
        return {"repos_processed": 1}


class FakeProService:
    def __init__(self) -> None:
        self.maintenance = FakeMaintenance()


def test_work_command_outputs_summary(monkeypatch) -> None:
    monkeypatch.setattr(cli, "_pro_service", lambda: FakeProService())
    result = CliRunner().invoke(cli.app, ["work"])
    assert result.exit_code == 0
    assert "repos_processed" in result.stdout
