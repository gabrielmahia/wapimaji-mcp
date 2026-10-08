# 💧 WapiMaji MCP — Kenya Water & Drought Intelligence
<!-- mcp-name: io.github.gabrielmahia/wapimaji-mcp -->

[![wapimaji-mcp Glama score](https://glama.ai/mcp/servers/gabrielmahia/wapimaji-mcp/badges/score.svg)](https://glama.ai/mcp/servers/gabrielmahia/wapimaji-mcp)
[![smithery badge](https://smithery.ai/badge/@gabrielmahia/wapimaji-mcp)](https://smithery.ai/server/@gabrielmahia/wapimaji-mcp)


---
**Compatible with `claude-sonnet-5`** (released 2026-06-30) — Anthropic's most agentic
Sonnet yet. Runs multi-step tool chains end-to-end without stopping short.
Install: `pip install wapimaji-mcp` · Use with any MCP client.

---


> A Kenya drought-response toolkit for AI agents: **simulated** county drought phases (no real NDMA data is integrated yet), SMS alerts through Africa's Talking that need explicit confirmation, and drought events published to the coordination bus.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green)](https://modelcontextprotocol.io)

## What it does, and does not

- **Simulated drought phases for the 47 counties.** Values are generated from the county name so downstream flows can be built and tested. They are **not observations** and not NDMA data; every answer says `"synthetic": true`. Never use them for decisions.
- **No real data source is integrated.** With `SANDBOX=false` the status tools return an explicit "not implemented, status unknown" error. NDMA publishes drought phases as periodic bulletins; FEWS NET and IPC publish food-security classifications through APIs that were slow or unverified when checked on 2026-10-07. Integrating one is the next step.
- **SMS alerts** through Africa's Talking: simulated by default (`sent: false`); a live send needs `SANDBOX=false` and `confirm_send=true`.
- **Coordination:** publish a drought event so downstream MCP servers (insurance, agriculture advisory, health, county alerts) can react.

## Tools

| Tool | Type | Description |
|------|------|-------------|
| `get_drought_status` | Read-only, simulated | A simulated drought phase for one county, labelled synthetic |
| `get_drought_alerts` | Read-only, simulated | Simulated list of counties at or above a phase |
| `sms_drought_alert` | Sends SMS | Send a drought alert SMS via Africa's Talking (needs `confirm_send=true` in live mode) |
| `publish_drought_coordination` | Writes an event | Publish a drought coordination event for downstream servers |

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

### Runtime safety and data limits

`SANDBOX=true` (the default) uses simulated county drought values, including
aggregate alerts. These values are not observations from NDMA. Live aggregate
alerts are not implemented and return an explicit error with unknown status.

SMS calls in sandbox return `sent: false` without contacting Africa's Talking.
Live SMS requires both `SANDBOX=false` and `confirm_send=true`, supplied only after
the user explicitly confirms that send. Provider acceptance does not establish
delivery to the recipient.

No real data source is integrated. Earlier versions listed NDMA, the Kenya Meteorological Department and FEWS NET here; the code never used them.

## Related

- [mpesa-mcp](https://pypi.org/project/mpesa-mcp/) — M-Pesa + Africa's Talking MCP server
- [WapiMaji](https://wapimaji.streamlit.app) — The Streamlit dashboard version
- [gabrielmahia.github.io](https://gabrielmahia.github.io) — Full civic portfolio

## IP & Collaboration

© 2026 Gabriel Mahia · [contact@aikungfu.dev](mailto:contact@aikungfu.dev)
License: MIT
Not affiliated with NDMA or Africa's Talking.


## Related datasets

Earlier versions said this server draws on NASA MODIS NDVI, NOAA CHIRPS, TRMM and FEWS NET; it does not read any of them. The Hugging Face datasets [africa-open-climate-data](https://huggingface.co/datasets/gmahia/africa-open-climate-data) and [east-africa-agricultural-pd](https://huggingface.co/datasets/gmahia/east-africa-agricultural-pd) are separate resources.

## Part of the East Africa Coordination Stack

This MCP server is part of the Kenya coordination infrastructure.
Connect it to [`africa-coord-bus`](https://github.com/gabrielmahia/africa-coord-bus) —
the coordination event bus that routes signals between domains automatically.

```bash
pip install africa-coord-bus
```

All servers: [pypi.org/user/gmahia](https://pypi.org/user/gmahia/)
Live demo: [coord-cascade-demo](https://github.com/gabrielmahia/coord-cascade-demo)

<!-- interconnect:v1 -->
## Part of the East Africa coordination stack

- **Install & run:** `pip install reli-cli && reli list` — the MCP servers on the [official MCP Registry](https://registry.modelcontextprotocol.io) under `io.github.gabrielmahia`
- **Evaluate any model on Swahili agent tasks:** [kipimo](https://github.com/gabrielmahia/kipimo) · [dataset](https://huggingface.co/datasets/gmahia/kipimo) · [leaderboard](https://huggingface.co/spaces/gmahia/kipimo-leaderboard)
- **Coordinate across servers:** [africa-coord-bus](https://pypi.org/project/africa-coord-bus/) — offline-first event bus with a built-in Kenya routing table
- **Datasets:** [huggingface.co/gmahia](https://huggingface.co/gmahia) · **Docs hub:** [nairobi-stack](https://github.com/gabrielmahia/nairobi-stack)

Model-agnostic by design: closed APIs, open-weight models, and small distilled models are all first-class citizens.
<!-- /interconnect:v1 -->
