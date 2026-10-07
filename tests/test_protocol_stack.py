"""The server must run on the standalone FastMCP (which serves both MCP protocol eras, including the stateless 2026-07-28 revision), not on the
mcp.server.fastmcp module that MCP SDK 2.0 removed. The tools a real client sees must equal the ones glama.json advertises."""
import asyncio
import json
import pathlib

from fastmcp import Client

from wapimaji_mcp import server

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_the_source_no_longer_imports_the_removed_sdk_module():
    assert "mcp.server.fastmcp" not in (ROOT / "src" / "wapimaji_mcp" / "server.py").read_text(encoding="utf-8")
    assert "from fastmcp import FastMCP" in (ROOT / "src" / "wapimaji_mcp" / "server.py").read_text(encoding="utf-8")


def test_a_real_client_lists_exactly_the_tools_glama_json_advertises():
    async def names():
        async with Client(server.mcp) as c:
            return sorted(t.name for t in await c.list_tools())
    advertised = sorted(t["name"] for t in json.loads((ROOT / "glama.json").read_text(encoding="utf-8"))["tools"])
    assert asyncio.run(names()) == advertised
