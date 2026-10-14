from wapimaji_mcp import server

_fn = lambda name: (getattr(server, name).fn if hasattr(getattr(server, name), "fn") else getattr(server, name))


import sys
import types


def test_live_sms_without_confirmation_is_refused_and_never_reaches_the_provider(monkeypatch):
    called = []
    monkeypatch.setitem(sys.modules, "africastalking", types.SimpleNamespace(initialize=lambda *a: called.append("init"), SMS=types.SimpleNamespace(send=lambda *a, **k: called.append("send"))))
    monkeypatch.setenv("SANDBOX", "false")
    r = _fn("sms_drought_alert")(["+254700000001"], "x", "WAPIMAJI", False)
    assert r["sent"] is False and "confirm_send" in r["error"] and called == []


def test_the_sandbox_simulates_and_reports_the_recipient_count(monkeypatch):
    monkeypatch.setenv("SANDBOX", "true")
    r = _fn("sms_drought_alert")(["+254700000001", "+254700000002"], "x", "WAPIMAJI", True)
    assert r["sent"] is False and r["sandbox"] is True and r["count"] == 2
