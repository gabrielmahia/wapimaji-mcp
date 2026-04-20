"""Smoke tests for wapimaji-mcp server."""
import os
os.environ["SANDBOX"] = "true"
os.environ["AT_USERNAME"] = "sandbox"
os.environ["AT_API_KEY"] = "test_key"

from wapimaji_mcp.server import get_drought_status, get_drought_alerts

def test_drought_status_nairobi():
    result = get_drought_status("Nairobi")
    assert "phase" in result
    assert 1 <= result["phase"] <= 5

def test_drought_status_invalid():
    result = get_drought_status("NotACounty")
    assert "error" in result

def test_drought_alerts_phase3():
    result = get_drought_alerts(3)
    assert "counties_at_phase" in result
    assert isinstance(result["count"], int)
