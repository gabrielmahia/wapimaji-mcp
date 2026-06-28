"""
Coordination event publishing for wapimaji-mcp.

When drought phase reaches WARNING threshold, publishes a CoordinationEvent
to africa-coord-bus so downstream MCP servers can respond:
  - bima-mcp: evaluate parametric insurance payouts
  - kilimo-mcp: issue drought-resistant crop advisory
  - afya-mcp: activate malnutrition surveillance
  - county-mcp: alert county health office

Optional: only active when africa-coord-bus is installed.
Set COORD_BUS_QUEUE env var to path for offline event queue.
"""
import os

_BUS = None
_HAS_BUS = False

def _get_bus():
    global _BUS, _HAS_BUS
    if _BUS is not None:
        return _BUS
    try:
        from africa_coord_bus import EventBus
        queue_path = os.getenv("COORD_BUS_QUEUE", "/tmp/wapimaji-coord-bus.jsonl")
        _BUS = EventBus(queue_path=queue_path)
        _HAS_BUS = True
    except ImportError:
        _HAS_BUS = False
    return _BUS


def publish_drought_event(county: str, county_code: int, phase: int,
                          rainfall_deficit_pct: float, ndvi_anomaly: float = 0.0,
                          spi_3month: float = 0.0) -> dict:
    """
    Publish a drought coordination event to africa-coord-bus.
    Phase 2+ → WARNING. Phase 3+ → ALERT. Phase 4+ → CRITICAL.
    Returns {"published": True/False, "targets": [...], "reason": "..."}.
    """
    bus = _get_bus()
    if not bus:
        return {"published": False, "reason": "africa-coord-bus not installed (pip install africa-coord-bus)"}

    try:
        from africa_coord_bus import CoordinationEvent, EventDomain, EventSeverity, KenyaLocation
    except ImportError:
        return {"published": False, "reason": "africa-coord-bus import failed"}

    # Map NDMA phase to coordination severity
    if phase >= 4:
        severity = EventSeverity.CRITICAL
    elif phase >= 3:
        severity = EventSeverity.ALERT
    elif phase >= 2:
        severity = EventSeverity.WARNING
    else:
        return {"published": False, "reason": f"Phase {phase} (Minimal) — no coordination needed"}

    event = CoordinationEvent(
        domain=EventDomain.WATER,
        event_type="drought_alert",
        source="wapimaji-mcp",
        severity=severity,
        location=KenyaLocation(county=county, county_code=county_code),
        data={
            "ndma_phase": phase,
            "phase_label": {1:"Minimal",2:"Stressed",3:"Crisis",4:"Emergency",5:"Famine"}.get(phase,"Unknown"),
            "rainfall_deficit_pct": rainfall_deficit_pct,
            "ndvi_anomaly": ndvi_anomaly,
            "spi_3month": spi_3month,
        },
        cross_domain_refs=[
            "finance.parametric_insurance_eval",
            "agriculture.drought_advisory",
            "health.malnutrition_watch",
        ],
        requires_action=True,
    )

    targets = bus.publish(event)
    return {
        "published": True,
        "event_id": event.event_id,
        "severity": severity.value,
        "county": county,
        "targets": targets,
        "target_count": len(targets),
    }
