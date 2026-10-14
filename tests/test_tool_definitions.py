"""Tool definitions are what an agent reads before choosing a tool (Glama scores them; server score = 60% mean + 40% worst tool)."""
import asyncio
import re

from fastmcp import Client

from wapimaji_mcp import server


def _tools():
    async def go():
        async with Client(server.mcp) as c:
            return await c.list_tools()
    return asyncio.run(go())


def test_every_tool_description_says_when_to_use_it_and_what_it_returns():
    for t in _tools():
        d = t.description or ""
        assert len(d) >= 250, (t.name, len(d))
        assert re.search(r"Use (when|only|before|first)|Takes no arguments", d), t.name
        assert "Returns" in d, t.name


def test_read_only_tools_say_so_and_tools_with_side_effects_say_what_they_do():
    for t in _tools():
        d, ann = t.description or "", (t.annotations.model_dump() if t.annotations else {})
        if ann.get("read_only_hint"):
            assert "Read-only" in d, t.name
        else:
            assert "Read-only" not in d, t.name
            assert re.search(r"Side effect|SENDS|Creates|Records|Adds|held in memory|emits", d), t.name


def test_every_parameter_has_a_description():
    for t in _tools():
        for name, prop in (t.inputSchema.get("properties") or {}).items():
            assert prop.get("description"), (t.name, name)
