"""Live tools say they are read-only and that they contact an outside service: clients use these hints to decide what is safe to auto-approve."""
import asyncio

from fastmcp import Client

from wapimaji_mcp import server


def test_every_live_tool_is_read_only_and_says_it_contacts_an_outside_service():
    async def tools():
        async with Client(server.mcp) as c:
            return await c.list_tools()
    ts = {t.name: t for t in asyncio.run(tools())}
    assert server.LIVE_TOOLS <= set(ts)
    for name in server.LIVE_TOOLS:
        a = ts[name].annotations
        assert a is not None and a.read_only_hint is True and a.open_world_hint is True, name
