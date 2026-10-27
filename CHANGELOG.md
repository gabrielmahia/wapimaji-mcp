## 0.1.16
- Security hardening from a static sweep: the default event-queue file is now per-user and owner-only (it was a fixed path in the shared `/tmp`); the two MD5 calls that derive simulated drought phases now say they are not for security (`usedforsecurity=False`; the phases are unchanged). `SECURITY.md` now holds the required reporting block and no longer says the data is real (it is simulated). 4 new tests.

## [0.1.3] — 2026-06-28

## 0.1.15
- The server reports its own version in the MCP handshake (it reported the FastMCP library version).
- Publishing: PyPI action pinned to a commit; `mcp-publisher` pinned and checksum-verified; registry step skipped when already published; least-privilege CI token.

### Added
- `coordination.py`: optional integration with africa-coord-bus
- `publish_drought_coordination` MCP tool — publishes drought events to coordination bus
- When drought phase ≥ 2, cascades to bima-mcp, kilimo-mcp, afya-mcp, county-mcp automatically
- Offline-first event queue via COORD_BUS_QUEUE environment variable

## [0.1.2] — 2026-06-04
### Changed
- Fixed glama.json schema URL to v1.0.0
- Added relatedServers: mpesa-mcp, swahili-health-mcp, civic-agent-kit
- Expanded tool descriptions for better Glama quality scoring
- Updated Docker build steps

## [0.1.1]
### Added
- Initial public release
- NDMA drought phase data for all 47 Kenya counties
- SMS alert dispatch via Africa's Talking

