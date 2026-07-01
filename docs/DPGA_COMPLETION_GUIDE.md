# DPGA Submission Guide — wapimaji-mcp (GID0093744)

**Status:** INCOMPLETE (as of July 1, 2026)  
**DPGA Registry:** https://digitalpublicgoods.net/registry/wapimaji-mcp.html

---

## What's missing to complete GID0093744

Based on the 2025 DPG Standard update (which now includes AI systems and
requires open training/testing data), the following are needed:

### 1. Open Data Documentation
The DPG Standard for AI systems (updated 2025) now requires:
- Open training and testing data, OR
- Clear documentation that no training data was used (tool-based MCP servers
  that wrap APIs do not train models, so this section can be completed with
  a statement of architecture)

**Action:** Add `DPGA_DATA_STATEMENT.md` stating: "This MCP server wraps public
APIs (NDMA, WRMA) and does not train or fine-tune any model. No proprietary
training data is used."

### 2. Open Standards Compliance
Document use of: MCP (AAIF/Linux Foundation open standard), JSON-RPC 2.0,
REST APIs. All standards used must be publicly accessible.

### 3. Do No Harm Documentation
Add a section to README explaining:
- Data privacy: what data is collected, how long it persists
- Inappropriate use prevention: this server provides environmental data, not
  personal data. Misuse vectors are limited but should be documented.

### 4. Extractability
Ensure all functionality can be accessed via the public PyPI package without
proprietary dependencies. This is already true for wapimaji-mcp but should
be explicitly documented.

---

## 2026 DPGA Context

The DPGA 2026 focus areas directly align with wapimaji-mcp:
- **Domain-specific DPGs in agriculture and climate** (Co-Develop 2025-2026 roadmap)
- **Open Data for Public Interest AI** (DPGA Call for Collaborative Action 2025)
- **AI systems as DPGs** — accepted as of 2025 standard update

The timing is favorable. Complete GID0093744 now while DPGA is actively sourcing
AI DPGs for SDG-relevant domains.

---

## Next Steps

1. Add `DPGA_DATA_STATEMENT.md` to this repo (template below)
2. Add Do No Harm section to README.md
3. Submit completion documentation at: https://digitalpublicgoods.net/submission/

### DPGA_DATA_STATEMENT.md template:

```markdown
# Data Statement — wapimaji-mcp (DPGA GID0093744)

## Architecture
wapimaji-mcp is an MCP server that wraps public APIs. It does not train,
fine-tune, or deploy any AI model. It exposes external data sources as
tools callable by AI agents.

## Data Sources
- Kenya National Drought Management Authority (NDMA) — public drought data
- Water Resources Management Authority (WRMA) — public water quality data
- Kenya Meteorological Department — public weather/forecast data

All source data is publicly available without registration or fee.

## No Training Data
This server contains no machine learning model and uses no training data.
The "AI" in its application context is the language model calling its tools
(e.g., Claude Sonnet 5), not any model embedded in this package.

## Privacy
No personal data is collected, stored, or transmitted by this server.
All queries are environmental/geographic, not personal.
```

*Last updated: July 1, 2026*
