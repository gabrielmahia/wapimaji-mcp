# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅         |
| < 0.1   | ❌         |

## Reporting a Vulnerability

If you discover an error:

DO NOT open a public issue.

Email directly to:
contact@aikungfu.dev

## Security Design Alignment

wapimaji-mcp is designed in alignment with:
- **NSA CSI U/OO/6030316-26 (May 2026)** — Model Context Protocol: Security Design Considerations
- **OWASP A08:2017** — Insecure Deserialization (mitigated via strict input validation)
- **Kenya CBK and WRMA data governance requirements** (drought and water stress data)

### NSA MCP Security Controls — Implementation Status

| NSA Recommendation | Status | Implementation |
|---|---|---|
| Access control / authentication | ✅ | Environment-variable credentials only; no hardcoded secrets |
| Parameter validation | ✅ | County names validated against known Kenya county list; coordinates range-checked |
| Audit logging | ✅ | Structured log entry per tool invocation; no PII collected |
| Token lifecycle | ✅ | API tokens cached with TTL; refreshed before each request |
| Sandbox / production isolation | ✅ | `WAPIMAJI_ENV=sandbox/production` flag enforced |
| HTTPS enforcement | ✅ | All upstream API calls use `https://`; no HTTP fallback |
| Error containment | ✅ | Tool handlers return structured error dicts; no raw exception propagation |
| No hardcoded secrets | ✅ | All credentials via environment variables |
| Input injection prevention | ✅ | County parameters validated against allowlist before query execution |

### Known Limitations (Protocol-Level)

- **Session authentication**: Not enforced at the MCP protocol level — this is a known gap in the MCP specification itself (ref: NSA CSI U/OO/6030316-26 §Access Control). Operator responsibility.
- **SIEM integration**: Audit logs go to stdout. Production deployments should pipe to a structured logging system.

## Data Classification

wapimaji-mcp handles **public environmental data** only:
- Kenya county-level water stress indices (WRMA open data)
- Drought severity grids (NDMA Kenya open data)
- No PII, no financial data, no authentication credentials in transit

## Reference

NSA Cybersecurity Information Sheet: [CSI_MCP_SECURITY.pdf](https://www.nsa.gov/Portals/75/documents/Cybersecurity/CSI_MCP_SECURITY.pdf)
Published: May 2026 | Classification: UNCLASSIFIED
