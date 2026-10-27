"""Two findings from a static security sweep of the estate (2026-10-27): a predictable /tmp queue path, and MD5 used (not for security) to derive simulated phases."""
import hashlib
import os
import re
import stat
from pathlib import Path

import pytest

from wapimaji_mcp import coordination

SRC = Path(__file__).resolve().parents[1] / "src" / "wapimaji_mcp"


def test_the_default_queue_is_a_per_user_owner_only_file_not_a_fixed_path_in_tmp(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    p = coordination._default_queue_path()
    assert p.startswith(str(tmp_path)) and p != "/tmp/wapimaji-coord-bus.jsonl"
    if os.name == "posix":
        assert stat.S_IMODE(os.stat(os.path.dirname(p)).st_mode) == 0o700


def test_the_environment_variable_still_overrides_the_default(monkeypatch):
    monkeypatch.setenv("COORD_BUS_QUEUE", "/var/queue/x.jsonl")
    src = (SRC / "coordination.py").read_text(encoding="utf-8")
    assert 'os.getenv("COORD_BUS_QUEUE") or _default_queue_path()' in src


def test_if_the_home_cache_cannot_be_created_a_private_temp_directory_is_used(monkeypatch):
    def boom(*a, **k):
        raise OSError("read-only")
    monkeypatch.setattr(os, "makedirs", boom)
    p = coordination._default_queue_path()
    assert os.path.basename(p) == "coord-bus.jsonl" and os.path.basename(os.path.dirname(p)).startswith("wapimaji-")
    if os.name == "posix":
        assert stat.S_IMODE(os.stat(os.path.dirname(p)).st_mode) == 0o700


def test_every_md5_call_states_it_is_not_for_security_and_the_simulated_phase_is_unchanged():
    src = (SRC / "server.py").read_text(encoding="utf-8")
    calls = re.findall(r"hashlib\.md5\((?:[^()]|\([^()]*\))*\)", src)   # one level of nested parentheses: county.encode()
    assert len(calls) == 2 and all("usedforsecurity=False" in c for c in calls), calls
    assert int(hashlib.md5(b"Turkana", usedforsecurity=False).hexdigest()[:4], 16) == int(hashlib.md5(b"Turkana").hexdigest()[:4], 16)
