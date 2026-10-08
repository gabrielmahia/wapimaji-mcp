"""The server must not present simulated drought values as NDMA data, must not call an unverified endpoint, and must tell clients which tools are safe."""
import asyncio
import pathlib
import re

from fastmcp import Client

from wapimaji_mcp import server

ROOT = pathlib.Path(__file__).resolve().parents[1]
call = lambda fn, *a, **k: (getattr(server, fn).fn if hasattr(getattr(server, fn), "fn") else getattr(server, fn))(*a, **k)


def test_simulated_status_says_so_and_never_claims_to_be_ndma_data(monkeypatch):
    monkeypatch.setenv("SANDBOX", "true")
    r = call("get_drought_status", "Turkana")
    assert r["synthetic"] is True and "not NDMA data" in r["source"] and "NDMA Kenya" not in r["source"]


def test_live_mode_is_an_explicit_error_not_a_call_to_an_unverified_endpoint(monkeypatch):
    monkeypatch.setenv("SANDBOX", "false")
    import socket
    monkeypatch.setattr(socket, "create_connection", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no network call is allowed")))
    r = call("get_drought_status", "Turkana")
    assert "not implemented" in r["error"] and r["sandbox"] is False


def test_clients_are_told_which_tools_are_safe_to_auto_approve():
    async def ann():
        async with Client(server.mcp) as c:
            return {t.name: t.annotations for t in await c.list_tools()}
    a = asyncio.run(ann())
    assert a["get_drought_status"].readOnlyHint is True and a["get_drought_alerts"].readOnlyHint is True
    assert a["sms_drought_alert"].readOnlyHint is False and a["sms_drought_alert"].openWorldHint is True
    assert a["publish_drought_coordination"].readOnlyHint is False


def test_the_readme_tool_table_lists_only_tools_that_exist_and_all_of_them():
    async def names():
        async with Client(server.mcp) as c:
            return {t.name for t in await c.list_tools()}
    real = asyncio.run(names())
    listed = set(re.findall(r"^\|\s*`([a-z_]+)`\s*\|", (ROOT / "README.md").read_text(encoding="utf-8"), re.MULTILINE))
    assert listed == real, (listed ^ real)


def test_no_real_data_source_is_claimed_anywhere():
    text = (ROOT / "README.md").read_text(encoding="utf-8") + (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "real-time access" not in text and "simulated" in text.lower()
    assert "NASA MODIS" not in text.split("## Related datasets")[0] and "draws on open" not in text
