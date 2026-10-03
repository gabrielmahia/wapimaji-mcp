"""Provider-free regressions for sandbox and explicit sending authority."""
import sys
from types import SimpleNamespace

from wapimaji_mcp.server import get_drought_alerts, sms_drought_alert


def forbidden(*args, **kwargs):
    raise AssertionError("Provider must not be invoked")


def test_default_sandbox_never_initializes_provider(monkeypatch):
    monkeypatch.delenv("SANDBOX", raising=False)
    monkeypatch.setenv("AT_USERNAME", "live-account")
    monkeypatch.setenv("AT_API_KEY", "not-a-real-key")
    monkeypatch.setitem(sys.modules, "africastalking", SimpleNamespace(initialize=forbidden))
    result = sms_drought_alert(["+254700000000"], "test")
    assert result.get("sandbox") is True
    assert result.get("sent") is False
    assert "error" not in result


def test_sandbox_confirmation_cannot_enable_provider(monkeypatch):
    monkeypatch.setenv("SANDBOX", "true")
    monkeypatch.setitem(sys.modules, "africastalking", SimpleNamespace(initialize=forbidden))
    result = sms_drought_alert([], "test", confirm_send=True)
    assert result.get("sandbox") is True
    assert result.get("sent") is False


def test_live_requires_explicit_boolean_confirmation(monkeypatch):
    monkeypatch.setenv("SANDBOX", "false")
    monkeypatch.setitem(sys.modules, "africastalking", SimpleNamespace(initialize=forbidden))
    for confirm in (None, False, "true", 1):
        result = sms_drought_alert([], "test", confirm_send=confirm)
        assert result.get("sent") is False
        assert "confirmation" in result.get("error", "").lower()


def test_confirmed_live_uses_stub_provider(monkeypatch):
    calls = []
    monkeypatch.setenv("SANDBOX", "false")
    monkeypatch.setenv("AT_USERNAME", "live-account")
    stub = SimpleNamespace(
        initialize=lambda *args: calls.append("initialize"),
        SMS=SimpleNamespace(send=lambda *args, **kwargs: calls.append("send") or {"stub": True}),
    )
    monkeypatch.setitem(sys.modules, "africastalking", stub)
    result = sms_drought_alert([], "test", confirm_send=True)
    assert result["sent"] is True
    assert calls == ["initialize", "send"]
    assert result["response"] == {"stub": True}


def test_alerts_identify_sandbox_simulation(monkeypatch):
    monkeypatch.setenv("SANDBOX", "true")
    result = get_drought_alerts(3)
    assert result.get("sandbox") is True
    assert "simulation" in result.get("source", "").lower()


def test_live_alerts_never_fabricate_counties(monkeypatch):
    monkeypatch.setenv("SANDBOX", "false")
    result = get_drought_alerts(3)
    assert "error" in result
    assert "counties_at_phase" not in result
