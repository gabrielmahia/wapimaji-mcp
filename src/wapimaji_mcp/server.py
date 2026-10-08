"""
WapiMaji MCP — a Kenya drought-response toolkit: SIMULATED county drought phases (no real NDMA data is integrated), SMS alerts that need explicit
confirmation, and coordination events. The simulated values are generated from the county name; they are not observations.
"""
import json
import os

from fastmcp import FastMCP

from wapimaji_mcp.coordination import publish_drought_event

mcp = FastMCP("wapimaji-mcp")

# Annotations tell clients which tools are safe to auto-approve. The simulated reads touch nothing; SMS and event publishing do not.
READ_ONLY = {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": False}
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


@mcp.tool(annotations=READ_ONLY)
def get_drought_status(county: str) -> dict:
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
        h = int(hashlib.md5(county.encode()).hexdigest()[:4], 16) % 4 + 1
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


@mcp.tool(annotations=READ_ONLY)
def get_drought_alerts(min_phase: int = 3) -> dict:
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
        h = int(hashlib.md5(county.encode()).hexdigest()[:4], 16) % 4 + 1
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


@mcp.tool(annotations=SENDS_SMS)
def sms_drought_alert(
    phone_numbers: list,
    message: str,
    sender_id: str = "WAPIMAJI",
    confirm_send: bool = False,
) -> dict:
    """
    Send a drought alert SMS via Africa's Talking.
    DESTRUCTIVE — sends real SMS only with SANDBOX=false and confirm_send=true.
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


def main():
    mcp.run()


if __name__ == "__main__":
    main()


@mcp.tool(annotations=WRITES_EVENT)
def publish_drought_coordination(county: str, phase: int = 0,
                                  rainfall_deficit_pct: float = 0.0) -> dict:
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
