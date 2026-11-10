"""A model-supplied confirm_send is not an independent check, so live SMS also needs operator-side limits the model cannot change:
an allowlist (empty by default = live sending off), a per-call cap and the 160-character limit. The provider must never be reached on a refusal."""
import sys
from types import SimpleNamespace

import pytest

from wapimaji_mcp.server import sms_drought_alert

OK = "+254700000001"


@pytest.fixture
def provider(monkeypatch):
    calls = []
    stub = SimpleNamespace(initialize=lambda *a: calls.append("initialize"), SMS=SimpleNamespace(send=lambda *a, **k: calls.append(("send", a[1])) or {"stub": True}))
    monkeypatch.setitem(sys.modules, "africastalking", stub)
    monkeypatch.setenv("SANDBOX", "false")
    monkeypatch.setenv("AT_USERNAME", "live-account")
    monkeypatch.delenv("WAPIMAJI_SMS_ALLOWLIST", raising=False)
    monkeypatch.delenv("WAPIMAJI_MAX_SMS_RECIPIENTS", raising=False)
    return calls


def test_by_default_live_sending_is_off_even_with_confirm_send(provider):
    r = sms_drought_alert([OK], "Drought alert", confirm_send=True)
    assert r["sent"] is False and "WAPIMAJI_SMS_ALLOWLIST" in r["error"] and provider == []


def test_a_recipient_outside_the_allowlist_blocks_the_whole_send(provider, monkeypatch):
    monkeypatch.setenv("WAPIMAJI_SMS_ALLOWLIST", f"{OK}, +254700000002")
    r = sms_drought_alert([OK, "+254799999999"], "Drought alert", confirm_send=True)
    assert r["sent"] is False and "not on the operator's" in r["error"] and "+254799999999" in r["error"] and provider == []


def test_allowlisted_recipients_are_sent_to(provider, monkeypatch):
    monkeypatch.setenv("WAPIMAJI_SMS_ALLOWLIST", f"{OK}, +254700000002")
    r = sms_drought_alert([OK, "+254700000002"], "Drought alert", confirm_send=True)
    assert r["sent"] is True and r["count"] == 2 and provider[-1] == ("send", [OK, "+254700000002"])


def test_confirm_send_is_still_required_even_when_allowlisted(provider, monkeypatch):
    monkeypatch.setenv("WAPIMAJI_SMS_ALLOWLIST", OK)
    for flag in (False, None, "true", 1):
        assert sms_drought_alert([OK], "Drought alert", confirm_send=flag)["sent"] is False
    assert provider == []


def test_the_per_call_cap_applies_even_to_allowlisted_numbers(provider, monkeypatch):
    numbers = [f"+2547000000{i:02d}" for i in range(5)]
    monkeypatch.setenv("WAPIMAJI_SMS_ALLOWLIST", ",".join(numbers))
    monkeypatch.setenv("WAPIMAJI_MAX_SMS_RECIPIENTS", "3")
    r = sms_drought_alert(numbers, "Drought alert", confirm_send=True)
    assert r["sent"] is False and "per-call cap of 3" in r["error"] and provider == []


@pytest.mark.parametrize("bad", ["abc", "0", "-4", ""])
def test_a_bad_cap_setting_falls_back_to_the_default_not_to_unlimited(provider, monkeypatch, bad):
    numbers = [f"+2547000000{i:02d}" for i in range(25)]
    monkeypatch.setenv("WAPIMAJI_SMS_ALLOWLIST", ",".join(numbers))
    monkeypatch.setenv("WAPIMAJI_MAX_SMS_RECIPIENTS", bad)
    r = sms_drought_alert(numbers, "Drought alert", confirm_send=True)
    assert r["sent"] is False and "per-call cap of 20" in r["error"]


def test_the_160_character_limit_is_enforced(provider, monkeypatch):
    monkeypatch.setenv("WAPIMAJI_SMS_ALLOWLIST", OK)
    assert sms_drought_alert([OK], "x" * 161, confirm_send=True)["sent"] is False
    assert sms_drought_alert([OK], "x" * 160, confirm_send=True)["sent"] is True


@pytest.mark.parametrize("numbers,message", [([], "hi"), ([OK, 5], "hi"), (OK, "hi"), ([OK], ""), ([OK], "   ")])
def test_malformed_input_is_refused_before_the_provider(provider, monkeypatch, numbers, message):
    monkeypatch.setenv("WAPIMAJI_SMS_ALLOWLIST", OK)
    assert sms_drought_alert(numbers, message, confirm_send=True)["sent"] is False and provider == []


def test_the_sandbox_is_unchanged_and_never_needs_an_allowlist(monkeypatch):
    monkeypatch.setenv("SANDBOX", "true")
    r = sms_drought_alert([OK, "+254799999999"], "hi", confirm_send=True)
    assert r["sandbox"] is True and r["sent"] is False and r["count"] == 2
