# AGENTS.md — WapiMaji MCP

## Purpose
MCP server for Kenya water stress and drought intelligence. Exposes NDMA drought data and AT SMS capabilities to AI agents.

## Structure
- `src/wapimaji_mcp/server.py` — main FastMCP server, all tools defined here
- `pyproject.toml` — package definition for PyPI
- `tests/` — smoke tests

## Key rules
- Never fabricate drought data in production mode
- SMS tools require explicit user confirmation before sending
- SANDBOX=true is the default — must be explicitly set to false for live data/SMS
- Follow mpesa-mcp patterns for consistency
