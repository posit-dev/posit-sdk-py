from __future__ import annotations

import importlib.util
from pathlib import Path

_SCRIPT = Path(__file__).parents[1] / "scripts" / "update_connect_matrix.py"
_SPEC = importlib.util.spec_from_file_location("update_connect_matrix", _SCRIPT)
assert _SPEC is not None
assert _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

supported_versions_from_html = _MODULE.supported_versions_from_html
update_makefile = _MODULE.update_makefile


def test_supported_versions_from_html_uses_latest_patch_for_each_train():
    html = """
    <table>
      <tr><th>Supported Version</th><th>Supported Until</th></tr>
      <tr><td>2026.08</td><td>February 29, 2028</td></tr>
      <tr><td>2026.07</td><td>January 31, 2028</td></tr>
    </table>
    <h2>2026.08.0</h2>
    <h2>2026.08.1</h2>
    <h2>2026.07.0</h2>
    """

    assert supported_versions_from_html(html) == ["2026.08.1", "2026.07.0"]


def test_update_makefile_replaces_version_block(tmp_path):
    makefile = tmp_path / "Makefile"
    makefile.write_text("# Versions\nCONNECT_VERSIONS := \\\n\t2025.01.0\n\n.PHONY: latest\n")

    assert update_makefile(makefile, ["2026.08.1", "2026.07.0"])
    assert makefile.read_text() == (
        "# Versions\nCONNECT_VERSIONS := \\\n\t2026.08.1 \\\n\t2026.07.0\n\n.PHONY: latest\n"
    )
    assert not update_makefile(makefile, ["2026.08.1", "2026.07.0"])
