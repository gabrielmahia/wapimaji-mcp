# Data Statement — wapimaji-mcp (DPGA GID0093744)

## Architecture

wapimaji-mcp is an MCP server that wraps public Kenya water and environmental APIs.
It does not train, fine-tune, or deploy any AI model. It exposes external data
sources as MCP tools callable by AI agents such as Claude.

## Data Sources

All sources are publicly available without registration or fee:

| Source | Data | Availability |
|--------|------|-------------|
| Kenya NDMA | Drought severity, county alerts | Public API |
| WRMA | Water quality, river levels | Public reports |
| Kenya Met Dept | Weather, seasonal forecasts | Public bulletins |

## No Training Data

This server contains no machine learning model and uses no training data.
The AI context is the language model calling its tools (e.g., `claude-sonnet-5`),
not any model embedded in this package.

## Privacy

No personal data is collected, stored, or transmitted by this server.
All queries are environmental and geographic — not personal.

## Open Standards Used

- Model Context Protocol (MCP) — AAIF/Linux Foundation open standard (Dec 2025)
- JSON-RPC 2.0 — IETF public standard
- REST/HTTP — public standard

## DPGA Review

**GID0093744 — INCOMPLETE** (as of July 2026)

To complete: see `docs/DPGA_COMPLETION_GUIDE.md` in this repository.

*Last updated: July 2026*
