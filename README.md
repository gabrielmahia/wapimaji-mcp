# 💧 WapiMaji MCP — Kenya Water & Drought Intelligence

> MCP server giving AI agents real-time access to Kenya's water stress and drought data — all 47 counties, NDMA drought phase classifications, and SMS alert capability via Africa's Talking.

[![License: CC BY-NC-ND 4.0](https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green)](https://modelcontextprotocol.io)

## What it does

WapiMaji MCP exposes Kenya drought and water stress data as MCP tools. Any Claude, GPT-4, or MCP-compatible AI agent can now:

- Query live drought phase data for any of Kenya's 47 counties
- Get water stress indices from NDMA drought monitor
- Send SMS alerts to farmers via Africa's Talking when drought levels spike

**One-prompt examples:**

```
"What is the current drought phase in Marsabit County?"
→ Gets NDMA Phase 3 classification + rainfall deficit data

"Which counties are in drought emergency right now?"
→ Returns all counties at Phase 3+ with population affected

"SMS these 500 Garissa farmers: drought phase has escalated to 3"
→ Sends alerts via Africa's Talking across Safaricom + Airtel
```

## Tools

| Tool | Type | Description |
|------|------|-------------|
| `get_drought_status` | Read-only | Current NDMA drought phase for a county |
| `get_county_water_stress` | Read-only | Water stress index, rainfall deficit, river levels |
| `get_drought_alerts` | Read-only | All counties at or above a given drought phase |
| `sms_drought_alert` | Destructive | Send drought alert SMS via Africa's Talking |

## Install

```bash
pip install wapimaji-mcp
# or:
uvx wapimaji-mcp
```

## Configure

```json
{
  "mcpServers": {
    "wapimaji": {
      "command": "uvx",
      "args": ["wapimaji-mcp"],
      "env": {
        "AT_USERNAME": "your_username",
        "AT_API_KEY": "your_at_key",
        "SANDBOX": "true"
      }
    }
  }
}
```

## Data sources

- **NDMA** — National Drought Management Authority drought phase classifications
- **Kenya Meteorological Department** — rainfall data
- **FEWS NET** — Famine Early Warning System food security projections

## Related

- [mpesa-mcp](https://pypi.org/project/mpesa-mcp/) — M-Pesa + Africa's Talking MCP server (3,000+ downloads)
- [WapiMaji](https://wapimaji.streamlit.app) — The Streamlit dashboard version
- [gabrielmahia.github.io](https://gabrielmahia.github.io) — Full civic portfolio

## IP & Collaboration

© 2026 Gabriel Mahia · [contact@aikungfu.dev](mailto:contact@aikungfu.dev)
License: CC BY-NC-ND 4.0
Not affiliated with NDMA or Africa's Talking.
