from __future__ import annotations

from assist_er.pro.models import AIChangeSet


class CodeGenerator:
    def improve_file(self, path: str, content: str) -> AIChangeSet:
        updated = content
        if "TODO" in updated:
            updated = updated.replace("TODO", "DONE")
        if not updated.endswith("\n"):
            updated += "\n"
        return AIChangeSet(
            summary=f"Applied deterministic cleanups to {path}",
            file_updates={path: updated},
        )

    def generate_tests(self, module_name: str) -> AIChangeSet:
        test_path = f"tests/test_{module_name.replace('/', '_')}.py"
        template = (
            "def test_smoke() -> None:\n"
            "    assert True\n"
        )
        return AIChangeSet(
            summary=f"Generated smoke tests for {module_name}",
            file_updates={test_path: template},
        )
