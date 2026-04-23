from assist_er.pro.core.ai.codegen import CodeGenerator


def test_codegen_improves_todo_and_newline() -> None:
    result = CodeGenerator().improve_file("x.py", "# TODO")
    assert "DONE" in result.file_updates["x.py"]
    assert result.file_updates["x.py"].endswith("\n")
