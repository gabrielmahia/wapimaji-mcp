"""Live tools: parsing, provenance, validation and failure behaviour, with the network mocked (CI never depends on the services)."""
import urllib.error

from wapimaji_mcp import server


def _boom(url, params=None, timeout=20.0):
    raise urllib.error.URLError("down")

def test_river_discharge_forecast_parses_and_finds_the_peak(monkeypatch):
    monkeypatch.setattr(server, "_live_get", lambda url, params=None, timeout=20.0: {"daily": {"time": ["2026-11-04", "2026-11-05", "2026-11-06"], "river_discharge": [120.0, 340.5, None]}})
    r = server.river_discharge_forecast(-0.45, 39.65, 3)
    assert len(r["days"]) == 3 and r["peak"] == {"date": "2026-11-05", "discharge_m3s": 340.5}
    assert r["source"].startswith("LIVE") and "Global Flood Awareness System" in r["attribution"] and "Not an official flood warning" in r["note"]


def test_river_discharge_failure_and_bad_input_never_give_numbers(monkeypatch):
    monkeypatch.setattr(server, "_live_get", _boom)
    assert "error" in server.river_discharge_forecast(-0.45, 39.65) and "days" not in server.river_discharge_forecast(-0.45, 39.65)
    assert "error" in server.river_discharge_forecast(-0.45, 200) and "error" in server.river_discharge_forecast(-0.45, 39.65, days=0)

def test_rainfall_forecast_parses_and_names_its_source(monkeypatch):
    monkeypatch.setattr(server, "_live_get", lambda url, params=None, timeout=20.0: {"daily": {"time": ["2026-11-04", "2026-11-05"], "precipitation_sum": [2.5, 0.0], "precipitation_probability_max": [80, 10]}})
    r = server.rainfall_forecast(-1.29, 36.82, 2)
    assert r["days"] == [{"date": "2026-11-04", "rain_mm": 2.5, "chance_pct": 80}, {"date": "2026-11-05", "rain_mm": 0.0, "chance_pct": 10}] and r["total_rain_mm"] == 2.5
    assert r["source"].startswith("LIVE") and "Open-Meteo" in r["attribution"] and r["retrieved_at"]


def test_rainfall_forecast_failure_and_bad_input_never_give_a_forecast(monkeypatch):
    monkeypatch.setattr(server, "_live_get", _boom)
    assert "error" in server.rainfall_forecast(-1.29, 36.82) and "days" not in server.rainfall_forecast(-1.29, 36.82)
    assert "error" in server.rainfall_forecast(95, 36.8) and "error" in server.rainfall_forecast(-1.3, 36.8, days=40)
