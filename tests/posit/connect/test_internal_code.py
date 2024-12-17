from pathlib import Path

import pytest

here = Path(__file__).resolve().parent
root_dir = here.parent.parent.parent

tests_dir = root_dir / "tests"
src_dir = root_dir / "src"
integration_tests_dir = tests_dir / "integration" / "tests"


@pytest.mark.parametrize("path", [tests_dir, src_dir, integration_tests_dir])
def test_no_from_typing_imports(path: Path):
    for python_file in path.rglob("*.py"):
        file_txt = python_file.read_text()
        if "\nfrom typing import" in file_txt:
            raise ValueError(
                f"Found `from typing import` in {python_file.relative_to(root_dir)}. Please replace the import with `typing_extensions`."
            )
