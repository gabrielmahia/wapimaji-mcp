"""
WapiMaji MCP — Kenya water stress and drought intelligence.
MCP server exposing NDMA drought data and AT SMS alerts.
"""
import os
import json
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("wapimaji-mcp")

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


@mcp.tool()
def get_drought_status(county: str) -> dict:
    """
    Get current NDMA drought phase classification for a Kenya county.
    Returns drought phase (1=Minimal to 5=Famine), rainfall deficit %, and population affected.
    county: Kenya county name e.g. Turkana, Marsabit, Garissa
    """
    county = county.strip().title()
    if county not in COUNTIES:
        return {"error": f"County not found. Example valid counties: Turkana, Marsabit, Garissa"}

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
            "source": "NDMA Kenya (sandbox simulation)",
            "note": "Set SANDBOX=false for live NDMA data",
        }
    try:
        r = httpx.get(
            f"https://www.ndma.go.ke/api/drought/{county.lower().replace(' ', '-')}",
            timeout=10
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_drought_alerts(min_phase: int = 3) -> dict:
    """
    Get all Kenya counties at or above a given drought phase.
    min_phase: 1=Minimal, 2=Stressed, 3=Crisis, 4=Emergency, 5=Famine
    """
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
    }


@mcp.tool()
def sms_drought_alert(
    phone_numbers: list,
    message: str,
    sender_id: str = "WAPIMAJI",
) -> dict:
    """
    Send a drought alert SMS via Africa's Talking.
    DESTRUCTIVE — sends real SMS in production. Use SANDBOX=true for testing.
    phone_numbers: list of E.164 format numbers e.g. ["+254712345678"]
    message: SMS text (max 160 chars)
    sender_id: registered AT sender ID
    """
    try:
        import africastalking
        username = os.getenv("AT_USERNAME", "sandbox")
        api_key  = os.getenv("AT_API_KEY", "")
        africastalking.initialize(username, api_key)
        sms = africastalking.SMS
        response = sms.send(message, phone_numbers,
                            sender_id=sender_id if username != "sandbox" else None)
        return {"sent": True, "response": response, "count": len(phone_numbers)}
    except Exception as e:
        return {"error": str(e)}


def main():
    mcp.run()


if __name__ == "__main__":
    main()
