# Threat Model — wapimaji-mcp

Framework: OWASP MCP Top 10 (2025) | NSA/CISA "Deploying AI Systems Securely" (U/OO/143395-24)

## System
wapimaji-mcp is a stateless stdio MCP server. It reads public government data and returns structured JSON. No write operations to external systems except SMS dispatch (wapimaji-mcp).

## Key Threats and Mitigations

| Threat | OWASP MCP | Mitigation |
|--------|-----------|------------|
| Credential exposure | MCP01 | All credentials in env vars; never logged |
| Prompt injection via tool params | MCP02 | Inputs validated by type; no shell/SQL interpolation |
| Excessive scope | MCP03 | All tools are read-only (except sms_drought_alert); readOnlyHint declared |
| DoS | MCP10 | 10-30s timeouts on all API calls |

SMS alerts (sms_drought_alert) are the only write operation. Phone numbers are transmitted to Africa's Talking API and not stored. destructiveHint: true declared.

## Out of Scope
Third-party API security, MCP client security, network-level attacks.

*Threat model version: 1.0 | June 2026 | OWASP MCP Top 10 2025*
