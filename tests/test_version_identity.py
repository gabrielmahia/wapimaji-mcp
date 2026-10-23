"""One version, four places: pyproject, server.json, glama.json and what the running server reports must agree."""
import json
import pathlib
import re
from importlib.metadata import version

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _pyproject_version():
    return re.search(r'^version\s*=\s*"([^"]+)"', (ROOT / "pyproject.toml").read_text(encoding="utf-8"), re.MULTILINE).group(1)


def test_the_installed_package_matches_pyproject():
    assert version("wapimaji-mcp") == _pyproject_version()


def test_server_json_and_glama_json_carry_the_same_version():
    pv = _pyproject_version()
    srv = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
    assert srv["version"] == pv and all(p["version"] == pv for p in srv.get("packages", []))
    assert json.loads((ROOT / "glama.json").read_text(encoding="utf-8"))["version"] == pv


def test_the_running_server_reports_the_package_version_not_the_library_version():
    """serverInfo.version used to be FastMCP's own (4.1.3) on all 33 servers."""
    import wapimaji_mcp
    from wapimaji_mcp.server import mcp

    assert mcp.version == _pyproject_version()
    assert getattr(wapimaji_mcp, "__version__", _pyproject_version()) == _pyproject_version()
