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

<!-- coverage-adaptive-reasoning:v2 -->

## Coverage-Adaptive Reasoning v2

For consequential research, recommendations, investigations, analogy searches, forecasting, opportunity discovery, and canon building:

- A correct ranking inside an incomplete universe is still a failed answer.
- Separate candidate generation from candidate ranking.
- Materiality-gate the search: use the minimum useful set of orthogonal retrieval routes that could change the answer.
- Before closure ask what correct answer the current search method would be structurally incapable of finding.
- Treat aliases, language/geography, era, source class, format, genealogy, taxonomy, legal identity vs operational control/economic benefit, intermediaries, schema categories, null/failure cases, and negative space as potential blind spots when material.
- Maintain leading + competing + null explanations.
- Distinguish answer confidence from coverage confidence.
- “Nothing found” is not evidence of absence when coverage is low.
- Stop when additional independent search routes no longer materially change the candidate universe, hypotheses, decision, or next test.
- When an important miss occurs, repair the retrieval architecture via MISS → SENSOR REDESIGN; do not merely append the missed example.

<!-- v2 section appended 2026-10-28 from https://github.com/gabrielmahia/nairobi-stack/blob/main/docs/COVERAGE_ADAPTIVE_REASONING.md; the rest of this file is unchanged. -->
