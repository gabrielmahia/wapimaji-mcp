"""
WapiMaji MCP — a Kenya drought-response toolkit: SIMULATED county drought phases (no real NDMA data is integrated), SMS alerts that need explicit
confirmation, and coordination events. The simulated values are generated from the county name; they are not observations.
"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime, timedelta
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from wapimaji_mcp.coordination import publish_drought_event

try:
    _VERSION = _pkg_version("wapimaji-mcp")
except PackageNotFoundError:  # a source tree that was never installed
    _VERSION = "0+unknown"


mcp = FastMCP("wapimaji-mcp", version=_VERSION)

# Annotations tell clients which tools are safe to auto-approve. The simulated reads touch nothing; SMS and event publishing do not.
READ_ONLY = {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": False}
# Live SMS boundary. `confirm_send` is supplied by the model itself, so on its own it is not an independent check: a model could be talked into
# messaging anyone. These limits are set by the OPERATOR in the server's environment, which the model cannot change.
SMS_MAX_CHARS = 160
DEFAULT_SMS_RECIPIENT_CAP = 20


def _sms_allowlist() -> set:
    """WAPIMAJI_SMS_ALLOWLIST: comma-separated E.164 numbers that may receive a live SMS. Empty (the default) means live sending is off."""
    return {n.strip() for n in os.getenv("WAPIMAJI_SMS_ALLOWLIST", "").split(",") if n.strip()}


def _sms_cap() -> int:
    """WAPIMAJI_MAX_SMS_RECIPIENTS: per-call recipient cap in live mode (default 20; an invalid or non-positive value falls back to the default)."""
    try:
        value = int(os.getenv("WAPIMAJI_MAX_SMS_RECIPIENTS", ""))
    except ValueError:
        return DEFAULT_SMS_RECIPIENT_CAP
    return value if value >= 1 else DEFAULT_SMS_RECIPIENT_CAP


def _live_sms_refusal(phone_numbers, message):
    """None if a live SMS may go out; otherwise the refusal to return to the model."""
    if not isinstance(phone_numbers, list) or not phone_numbers or not all(isinstance(n, str) and n.strip() for n in phone_numbers):
        return {"sent": False, "error": "phone_numbers must be a non-empty list of E.164 number strings."}
    if not isinstance(message, str) or not message.strip():
        return {"sent": False, "error": "message must be non-empty text."}
    if len(message) > SMS_MAX_CHARS:
        return {"sent": False, "error": f"message is {len(message)} characters; the limit is {SMS_MAX_CHARS}."}
    if len(phone_numbers) > _sms_cap():
        return {"sent": False, "error": f"{len(phone_numbers)} recipients exceeds the per-call cap of {_sms_cap()} (operator setting WAPIMAJI_MAX_SMS_RECIPIENTS)."}
    allowed = _sms_allowlist()
    if not allowed:
        return {"sent": False, "error": "Live SMS is off until the operator sets WAPIMAJI_SMS_ALLOWLIST to the numbers that may receive alerts. The model cannot change this."}
    outside = [n for n in phone_numbers if n.strip() not in allowed]
    if outside:
        return {"sent": False, "error": f"{len(outside)} recipient(s) are not on the operator's WAPIMAJI_SMS_ALLOWLIST (for example {outside[0]}). Nothing was sent."}
    return None


SENDS_SMS = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": True}
WRITES_EVENT = {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False}

COUNTIES = [
    "Nairobi","Mombasa","Kwale","Kilifi","Tana River","Lamu","Taita Taveta",
    "Garissa","Wajir","Mandera","Marsabit","Isiolo","Meru","Tharaka Nithi",
    "Embu","Kitui","Machakos","Makueni","Nyandarua","Nyeri","Kirinyaga",
    "Murang'a","Kiambu","Turkana","West Pokot","Samburu","Trans Nzoia",
    "Uasin Gishu","Elgeyo Marakwet","Nandi","Baringo","Laikipia","Nakuru",
    "Narok","Kajiado","Kericho","Bomet","Kakamega","Vihiga","Bungoma",
    "Busia","Siaya","Kisumu","Homa Bay","Migori","Kisii","Nyamira",
]

DROUGHT_PHASES = {1: "Minimal", 2: "Stressed", 3: "Crisis", 4: "Emergency", 5: "Famine"}


@mcp.tool(description="SIMULATED drought phase for a Kenyan county: the values are generated from the county name, are NOT NDMA data and not an observation, and every answer says synthetic true. Use only to build and test flows, never for decisions. An unknown county returns an error; in live mode it returns an explicit not-implemented error because no data source is integrated. Returns county, phase, phase label, rainfall deficit percent, population affected, synthetic true, the source and a note. Read-only.", annotations=READ_ONLY)
def get_drought_status(county: Annotated[str, Field(description="Kenyan county name such as Turkana, Marsabit or Garissa.")]) -> dict:
    """
    Get a SIMULATED drought phase for a Kenya county. This is NOT NDMA data and not an observation: the values are generated from the county name
    so that downstream flows can be built and tested, and every answer says "synthetic": true. No real drought data source is integrated yet.
    Returns phase (1=Minimal to 5=Famine), rainfall deficit % and population affected, all simulated.
    county: Kenya county name e.g. Turkana, Marsabit, Garissa
    """
    county = county.strip().title()
    if county not in COUNTIES:
        return {"error": "County not found. Example valid counties: Turkana, Marsabit, Garissa"}

    sandbox = os.getenv("SANDBOX", "true").lower() == "true"
    if sandbox:
        import hashlib
        h = int(hashlib.md5(county.encode(), usedforsecurity=False).hexdigest()[:4], 16) % 4 + 1
        return {
            "county": county,
            "phase": h,
            "phase_label": DROUGHT_PHASES[h],
            "rainfall_deficit_pct": round(((h - 1) * 15) + 10, 1),
            "population_affected": (h - 1) * 50000 + 10000,
            "synthetic": True,
            "source": "SIMULATION generated from the county name: not NDMA data and not an observation",
            "note": "No verified drought data source is integrated; do not use for decisions.",
        }
    return {"error": "Live drought data is not implemented: no verified NDMA data API is integrated (NDMA publishes drought phases as periodic bulletins); status is unknown", "sandbox": False}


@mcp.tool(description="List SIMULATED county drought alerts at or above a minimum phase (1 minimal, 2 stressed, 3 crisis, 4 emergency, 5 famine; default 3). Use only to build and test flows: this is sandbox data, not NDMA observation, and production returns an explicit not-implemented error. Returns the counties at that phase with population affected, the count, the phase queried and its label, sandbox true and the source. Read-only.", annotations=READ_ONLY)
def get_drought_alerts(min_phase: Annotated[int, Field(description="Minimum phase: 1 minimal, 2 stressed, 3 crisis, 4 emergency, 5 famine (default 3).")] = 3) -> dict:
    """
    Get simulated Kenya county alerts in sandbox mode.
    Live aggregate drought data is not implemented; production fails explicitly.
    min_phase: 1=Minimal, 2=Stressed, 3=Crisis, 4=Emergency, 5=Famine
    """
    if os.getenv("SANDBOX", "true").lower() != "true":
        return {"error": "Live aggregate drought data is not implemented; status is unknown",
                "sandbox": False}
    import hashlib
    results = []
    for county in COUNTIES:
        h = int(hashlib.md5(county.encode(), usedforsecurity=False).hexdigest()[:4], 16) % 4 + 1
        if h >= min_phase:
            results.append({
                "county": county,
                "phase": h,
                "phase_label": DROUGHT_PHASES[h],
                "population_affected": (h - 1) * 50000 + 10000,
            })
    return {
        "counties_at_phase": results,
        "count": len(results),
        "min_phase_queried": min_phase,
        "phase_label": DROUGHT_PHASES.get(min_phase, "Unknown"),
        "sandbox": True,
        "source": "Sandbox simulation (not observed NDMA data)",
    }


@mcp.tool(description="Send a drought alert SMS through Africa's Talking. Use only when the user has explicitly approved this exact message and recipient list. SENDS TO REAL PEOPLE: real messages go out only when SANDBOX=false, confirm_send=true and every recipient is on the operator's WAPIMAJI_SMS_ALLOWLIST (empty by default, so live sending is off; at most 20 recipients per call); otherwise it simulates and reports the recipient count without contacting the provider. Returns sent, count and the provider response, or an error. Messages are limited to 160 characters. Sending cannot be undone.", annotations=SENDS_SMS)
def sms_drought_alert(
    phone_numbers: Annotated[list, Field(description="List of recipient numbers in E.164 format such as ['+254712345678'].")],
    message: Annotated[str, Field(description="SMS text, at most 160 characters.")],
    sender_id: Annotated[str, Field(description="Registered Africa's Talking sender ID (default WAPIMAJI).")] = "WAPIMAJI",
    confirm_send: Annotated[bool, Field(description="Set true only after the user explicitly approves this exact send; required for live sending.")] = False,
) -> dict:
    """
    Send a drought alert SMS via Africa's Talking.
    DESTRUCTIVE — sends real SMS only with SANDBOX=false, confirm_send=true and recipients on the operator's allowlist.
    Sandbox returns a simulation without contacting the provider.
    confirm_send: explicit user confirmation for this send; defaults to false.
    phone_numbers: list of E.164 format numbers e.g. ["+254712345678"]
    message: SMS text (max 160 chars)
    sender_id: registered AT sender ID
    """
    if os.getenv("SANDBOX", "true").lower() == "true":
        return {"sent": False, "sandbox": True, "count": len(phone_numbers),
                "note": "Sandbox simulation; no SMS sent"}
    if confirm_send is not True:
        return {"sent": False, "error": "Explicit user confirmation is required (confirm_send=true)"}
    refusal = _live_sms_refusal(phone_numbers, message)
    if refusal:
        return refusal
    try:
        import africastalking
        username = os.getenv("AT_USERNAME", "sandbox")
        api_key  = os.getenv("AT_API_KEY", "")
        africastalking.initialize(username, api_key)
        sms = africastalking.SMS
        response = sms.send(message, phone_numbers,
                            sender_id=sender_id if username != "sandbox" else None)
        return {"sent": True, "response": response, "count": len(phone_numbers)}
    except Exception as e:  # noqa: BLE001  (tool boundary: return the error to the model instead of crashing the server)
        return {"error": str(e)}



# ── Live data (free public services) ─────────────────────────────────
# Live tools change nothing anywhere, but they contact an outside service, and clients should know that.
LIVE_READ_ONLY = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": True}
LIVE_TOOLS = {"river_discharge_forecast", "rainfall_forecast"}
_LIVE_UA = {"User-Agent": "wapimaji-mcp (https://github.com/gabrielmahia/wapimaji-mcp)", "Accept": "application/json"}
_LIVE_ERRORS = (urllib.error.URLError, TimeoutError, ValueError, KeyError, TypeError, IndexError)


def _live_get(url: str, params: dict | None = None, timeout: float = 20.0):
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=_LIVE_UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:  # fixed https endpoints only
        return json.loads(r.read().decode("utf-8"))


def _live_meta(source: str, attribution: str) -> dict:
    return {"source": source, "attribution": attribution, "retrieved_at": datetime.now(UTC).isoformat(timespec="seconds")}

@mcp.tool(name="river_discharge_forecast", annotations=LIVE_READ_ONLY, description="Get the forecast daily river flow (discharge, cubic metres per second) at a point on a river, from the Copernicus Global Flood Awareness System (GloFAS) via the free Open-Meteo flood service. Use when someone is watching a river for flood risk, planning a crossing or water abstraction, or comparing this week's flow with the days ahead, for example on the Tana, Athi, Nzoia or Nyando. Returns one row per day, the peak day, the source, its attribution and the retrieval time; on a network or service failure it returns an error instead of numbers. Read-only; contacts an external service.")
def river_discharge_forecast(latitude: Annotated[float, Field(description="Latitude of a point on the river, in decimal degrees; between -90 and 90. Choose a point on the main channel.")],
                             longitude: Annotated[float, Field(description="Longitude of the point, in decimal degrees; between -180 and 180.")],
                             days: Annotated[int, Field(description="How many days ahead to forecast, between 1 and 30.")] = 7) -> dict:
    meta = _live_meta("LIVE — Copernicus GloFAS via the Open-Meteo flood API (flood-api.open-meteo.com)", "Copernicus Emergency Management Service, Global Flood Awareness System, via Open-Meteo.com, CC BY 4.0.")
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return {"error": "latitude must be between -90 and 90 and longitude between -180 and 180", **meta}
    if not 1 <= days <= 30:
        return {"error": "days must be between 1 and 30", **meta}
    try:
        d = _live_get("https://flood-api.open-meteo.com/v1/flood", {"latitude": latitude, "longitude": longitude, "daily": "river_discharge", "forecast_days": days})
        rows = [{"date": t, "discharge_m3s": q} for t, q in zip(d["daily"]["time"], d["daily"]["river_discharge"], strict=True)]
        if not rows:
            raise ValueError("empty forecast")
    except _LIVE_ERRORS as e:
        return {"error": f"the flood service did not return a usable forecast ({type(e).__name__}); no figures are given without it. Try again later.", **meta}
    valid = [r for r in rows if r["discharge_m3s"] is not None]
    peak = max(valid, key=lambda r: r["discharge_m3s"]) if valid else None
    return {"latitude": latitude, "longitude": longitude, "days": rows, "peak": peak,
            "note": "A 5 km model grid: small streams are not resolved, and a value near zero usually means the point is not on a modelled river. Not an official flood warning: follow the Kenya Meteorological Department and the Water Resources Authority.", **meta}

@mcp.tool(name="rainfall_forecast", annotations=LIVE_READ_ONLY, description="Get the daily rainfall forecast for a location in Kenya (or anywhere) for up to 16 days, from the free Open-Meteo weather service: expected millimetres and the chance of rain each day. Use when someone is planning planting, irrigation, water storage, travel or flood preparation and needs the rain outlook for a place. Returns one row per day with rain in mm and the maximum chance of rain in percent, the total, the source, its attribution and the retrieval time; on a network or service failure it returns an error instead of a forecast. Read-only; contacts an external service.")
def rainfall_forecast(latitude: Annotated[float, Field(description="Latitude in decimal degrees, for example -1.29 for Nairobi or -0.09 for Kisumu; between -90 and 90.")],
                      longitude: Annotated[float, Field(description="Longitude in decimal degrees, for example 36.82 for Nairobi; between -180 and 180.")],
                      days: Annotated[int, Field(description="How many days ahead to forecast, between 1 and 16.")] = 7) -> dict:
    meta = _live_meta("LIVE — Open-Meteo weather forecast API (api.open-meteo.com)", "Weather data by Open-Meteo.com, CC BY 4.0. The free API is for non-commercial use.")
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return {"error": "latitude must be between -90 and 90 and longitude between -180 and 180", **meta}
    if not 1 <= days <= 16:
        return {"error": "days must be between 1 and 16", **meta}
    try:
        d = _live_get("https://api.open-meteo.com/v1/forecast", {"latitude": latitude, "longitude": longitude, "daily": "precipitation_sum,precipitation_probability_max", "forecast_days": days, "timezone": "Africa/Nairobi"})
        daily = d["daily"]
        rows = [{"date": t, "rain_mm": r, "chance_pct": p} for t, r, p in zip(daily["time"], daily["precipitation_sum"], daily["precipitation_probability_max"], strict=True)]
        if not rows:
            raise ValueError("empty forecast")
    except _LIVE_ERRORS as e:
        return {"error": f"Open-Meteo did not return a usable forecast ({type(e).__name__}); no forecast is given without it. Try again later.", **meta}
    return {"latitude": latitude, "longitude": longitude, "days": rows, "total_rain_mm": round(sum(r["rain_mm"] or 0 for r in rows), 1),
            "note": "A model forecast: confidence falls with each day ahead, and local storms can differ from the grid forecast.", **meta}


def main():
    mcp.run()


if __name__ == "__main__":
    main()


@mcp.tool(description="Publish a drought coordination event to africa-coord-bus so other servers can react (insurance evaluation, advisories, malnutrition watch, county alerts). Use when coordinating a drought response across servers. Phases 2 stressed, 3 crisis and 4 emergency trigger coordination; phase 0 takes the phase and deficit from get_drought_status, which is SIMULATED data. Returns published false with a reason if africa-coord-bus is not installed. Side effect: emits an event to the bus.", annotations=WRITES_EVENT)
def publish_drought_coordination(county: Annotated[str, Field(description="Kenyan county name.")], phase: Annotated[int, Field(description="Drought phase 1-5; 0 (default) takes it from get_drought_status.")] = 0,
                                  rainfall_deficit_pct: Annotated[float, Field(description="Rainfall deficit in percent; used when phase is given (default 0).")] = 0.0) -> dict:
    """
    Publish a drought coordination event to africa-coord-bus so downstream
    MCP servers respond automatically (bima-mcp insurance eval, kilimo-mcp
    advisory, afya-mcp malnutrition watch, county-mcp alert).
    Phase 2=Stressed, 3=Crisis, 4=Emergency trigger coordination.
    """
    county_codes = {
        "Turkana": 23, "Marsabit": 22, "Wajir": 37, "Mandera": 29,
        "Garissa": 9, "Tana River": 28, "Kilifi": 25, "Kwale": 17,
    }
    code = county_codes.get(county.strip().title(), 0)
    if phase == 0:
        status = get_drought_status(county)
        phase = status.get("phase", 1)
        rainfall_deficit_pct = status.get("rainfall_deficit_pct", 0.0)
    return publish_drought_event(county.strip().title(), code, phase, rainfall_deficit_pct)
