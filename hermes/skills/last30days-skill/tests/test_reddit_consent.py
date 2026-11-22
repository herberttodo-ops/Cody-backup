"""Reddit session consent, the cookie read, and onboarding (plan U6, AE1, AE10).

Reading the reddit.com login cookie needs its own consent, separate from the
X browser consent, and every global refusal vetoes it. These tests watch the
cookie reader itself: a ``.reddit.com`` read is any ``extract_cookies`` call
for that domain.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

import pytest

import last30days as cli
from lib import cookie_extract, doctor, env, reddit_session, safari_cookies, setup_wizard

COOKIE = "dummy-reddit-cookie-value-___ID___"


class CookieSpy:
    """Stands in for cookie_extract.extract_cookies; records every domain read."""

    def __init__(self, logged_in=("chrome",)):
        self.logged_in = set(logged_in)
        self.calls: list[tuple[str, str]] = []

    def __call__(self, browser, domain, names):
        self.calls.append((browser, domain))
        if domain == env.REDDIT_COOKIE_DOMAIN and browser in self.logged_in:
            return {"reddit_session": COOKIE}
        return None

    def reddit_reads(self):
        return [b for b, d in self.calls if "reddit" in d]


@pytest.fixture
def spy(monkeypatch):
    s = CookieSpy()
    monkeypatch.setattr(cookie_extract, "extract_cookies", s)
    monkeypatch.setattr(env, "x_extras_enabled", lambda _c: False)
    return s


def _config(monkeypatch, mode="read", **values):
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    return env.get_config(policy=env.ConfigLoadPolicy(browser_cookies=mode))


def _session(config):
    return reddit_session.session_for(config)


class TestAE1:
    def test_x_consent_alone_never_reads_reddit(self, spy, monkeypatch):
        config = _config(monkeypatch, BROWSER_CONSENT="true", FROM_BROWSER="chrome")
        assert _session(config) is None
        assert spy.reddit_reads() == []
        assert any(d == ".x.com" for _b, d in spy.calls)  # X itself still reads

    def ___LONG_STRING___(self, spy, monkeypatch):
        config = _config(monkeypatch, REDDIT_BROWSER_CONSENT="true", REDDIT_FROM_BROWSER="chrome",
                         FROM_BROWSER="off")
        assert _session(config) is None
        assert spy.calls == []

    def test_reddit_yes_outranks_an_x_refusal(self, monkeypatch):
        config = _config(monkeypatch, REDDIT_BROWSER_CONSENT="true", REDDIT_FROM_BROWSER="chrome",
                         BROWSER_CONSENT="false")
        assert env.reddit_session_gate(config) == (True, "")

    def ___LONG_STRING___(self, spy, monkeypatch):
        config = _config(monkeypatch, REDDIT_FROM_BROWSER="chrome", BROWSER_CONSENT="false")
        assert _session(config) is None
        assert spy.reddit_reads() == []

    def ___LONG_STRING___(self, spy, monkeypatch):
        config = _config(monkeypatch, REDDIT_BROWSER_CONSENT="true", REDDIT_FROM_BROWSER="chrome",
                         FROM_BROWSER="off")
        assert _session(config) is None
        assert spy.reddit_reads() == []

    def ___LONG_STRING___(self, spy, monkeypatch):
        config = _config(monkeypatch, LAST30DAYS_HOST="grok-bot", LAST30DAYS_X_BACKEND="bird",
                         REDDIT_BROWSER_CONSENT="true", REDDIT_FROM_BROWSER="chrome", FROM_BROWSER="chrome")
        assert _session(config) is None
        assert spy.reddit_reads() == []
        assert env.reddit_session_gate(config) == (False, "never on a Grok Bot host")


class TestVetoesAndContexts:
    def ___LONG_STRING___(self, spy, monkeypatch):
        config = _config(monkeypatch, mode="plan_only", REDDIT_BROWSER_CONSENT="true",
                         REDDIT_FROM_BROWSER="chrome")
        allowed, why = env.reddit_session_gate(config)
        assert not allowed and "reads no browser cookies" in why
        assert _session(config) is None
        assert spy.calls == []

    def ___LONG_STRING___(self, spy, monkeypatch):
        config = _config(monkeypatch, mode="off", REDDIT_BROWSER_CONSENT="true", REDDIT_FROM_BROWSER="chrome")
        assert _session(config) is None and spy.calls == []

    def ___LONG_STRING___(self, spy, monkeypatch):
        config = _config(monkeypatch, REDDIT_BROWSER_CONSENT="false", REDDIT_FROM_BROWSER="chrome",
                         AGENTCOOKIE="on")
        assert _session(config) is None
        assert spy.reddit_reads() == []

    def test_hosted_backend_reads_nothing(self, spy, monkeypatch):
        monkeypatch.setenv("LAST30DAYS_API_KEY", "hosted-test-key")
        monkeypatch.setenv("LAST30DAYS_API_BASE", "https://hosted.example.test")
        config = _config(monkeypatch, REDDIT_BROWSER_CONSENT="true", REDDIT_FROM_BROWSER="chrome")
        assert env.reddit_session_gate(config)[1] == "the hosted API backend runs research remotely"
        assert _session(config) is None and spy.reddit_reads() == []

    def ___LONG_STRING___(self, spy, monkeypatch):
        monkeypatch.setenv("LAST30DAYS_SCHEDULED_RUN", "1")
        config = _config(monkeypatch, REDDIT_BROWSER_CONSENT="true", REDDIT_FROM_BROWSER="chrome")
        assert _session(config) is None and spy.reddit_reads() == []
        reddit_session.reset_run_state()
        config = _config(monkeypatch, LAST30DAYS_REDDIT_SESSION_SCHEDULED="1")
        assert _session(config) is not None
        assert spy.reddit_reads() == ["chrome"]

    def ___LONG_STRING___(self, monkeypatch, tmp_path):
        env.CONFIG_FILE.write_text("LAST30DAYS_SCHEDULED_RUN=1\n", encoding="utf-8")
        env.CONFIG_FILE.chmod(0o600)
        config = env.get_config()
        assert not config.get("LAST30DAYS_SCHEDULED_RUN")

    def ___LONG_STRING___(self, monkeypatch):
        import watchlist

        seen = {}

        def fake_run(argv, **kwargs):
            seen["argv"], seen["env"] = argv, kwargs["env"]
            raise RuntimeError("stop after capture")

        monkeypatch.setattr(watchlist.subprocess, "run", fake_run)
        monkeypatch.setattr(watchlist.store, "update_run", lambda *a, **k: None)
        with contextlib.suppress(Exception):
            watchlist._research_topic({"id": 1, "name": "x", "search_queries": None}, 1,
                                      {"LAST30DAYS_SCHEDULED_RUN": "1"})
        assert "--no-browser-cookies" in seen["argv"]
        assert seen["env"]["LAST30DAYS_SCHEDULED_RUN"] == "1"
        source = Path(watchlist.__file__).read_text(encoding="utf-8")
        assert '"LAST30DAYS_SCHEDULED_RUN": "1"' in source


class TestBrowserChoice:
    def ___LONG_STRING___(self, spy, monkeypatch):
        config = _config(monkeypatch, REDDIT_BROWSER_CONSENT="true", REDDIT_FROM_BROWSER="chrome")
        session = _session(config)
        assert session is not None and session.browser == "chrome"
        assert spy.reddit_reads() == ["chrome"]
        assert COOKIE not in repr(session) and COOKIE not in json.dumps(
            {k: str(v) for k, v in config.items()}
        )

    def ___LONG_STRING___(self, spy, monkeypatch):
        config = _config(monkeypatch, BROWSER_CONSENT="true", FROM_BROWSER="firefox",
                         REDDIT_BROWSER_CONSENT="true", REDDIT_FROM_BROWSER="chrome")
        assert _session(config) is not None
        assert ("chrome", env.REDDIT_COOKIE_DOMAIN) in spy.calls
        assert ("firefox", env.REDDIT_COOKIE_DOMAIN) not in spy.calls
        assert all(b == "firefox" for b, d in spy.calls if d == ".x.com")

    def ___LONG_STRING___(self, spy):
        env.extract_browser_credentials({"FROM_BROWSER": "chrome", env.REDDIT_CONSENT_VAR: "true"})
        assert spy.reddit_reads() == []

    def test_lookalike_host_cookie_is_rejected(self):
        assert safari_cookies._host_matches(".reddit.com", env.REDDIT_COOKIE_DOMAIN)
        assert safari_cookies._host_matches("www.reddit.com", env.REDDIT_COOKIE_DOMAIN)
        assert not safari_cookies._host_matches("reddit.com.evil.tld", env.REDDIT_COOKIE_DOMAIN)
        assert not safari_cookies._host_matches("notreddit.com", env.REDDIT_COOKIE_DOMAIN)

    def ___LONG_STRING___(self, monkeypatch):
        monkeypatch.setattr(env.os, "name", "nt")
        assert env.read_reddit_session_cookie({}, "chrome") == (None, "unsupported-encryption")


class TestSetup:
    def ___LONG_STRING___(self, spy, tmp_path):
        env_path = tmp_path / ".env"
        spy.logged_in = {"firefox"}
        result = setup_wizard.run_reddit_session_setup({}, env_path, consent=True)
        assert result["status"] == "found" and result["browser"] == "firefox"
        assert [c["browser"] for c in result["checked"]][0] == "chrome"
        text = env_path.read_text(encoding="utf-8")
        assert "REDDIT_BROWSER_CONSENT=true" in text
        assert "REDDIT_FROM_BROWSER=firefox" in text
        assert "REDDIT_SESSION_OFFERED=true" in text
        assert COOKIE not in text and COOKIE not in json.dumps(result)

    def ___LONG_STRING___(self, spy, tmp_path):
        env_path = tmp_path / ".env"
        result = setup_wizard.run_reddit_session_setup({}, env_path, consent=False)
        assert result["status"] == "declined" and spy.calls == []
        text = env_path.read_text(encoding="utf-8")
        assert "REDDIT_BROWSER_CONSENT=false" in text and "REDDIT_SESSION_OFFERED=true" in text

    def ___LONG_STRING___(self, spy, tmp_path):
        result = setup_wizard.run_reddit_session_setup({"FROM_BROWSER": "off"}, tmp_path / ".env", consent=True)
        assert result["status"] == "vetoed" and spy.calls == []

    def ___LONG_STRING___(self, spy, tmp_path):
        setup_wizard.run_reddit_session_setup({"BROWSER_CONSENT": "false"}, tmp_path / ".env", consent=True)
        assert spy.calls

    def ___LONG_STRING___(self, spy, tmp_path):
        env_path = tmp_path / ".env"
        result = setup_wizard.run_reddit_session_setup({"LAST30DAYS_HOST": "grok-bot"}, env_path, consent=True)
        assert result["status"] == "unavailable" and spy.calls == [] and not env_path.exists()

    def test_cli_setup_flag_is_a_passthrough(self):
        assert "--reddit-session" in cli.SETUP_PASSTHROUGH_FLAGS
        assert "--no-reddit-session" in cli.SETUP_PASSTHROUGH_FLAGS


class TestDoctorRow:
    def ___LONG_STRING___(self, spy):
        config = {env.REDDIT_CONSENT_VAR: "true", env.REDDIT_FROM_BROWSER_VAR: "chrome"}
        report = doctor.build_report(config)
        row = next(r for r in report["sources"]["reddit"]["paths"] if r["path"] == "session")
        assert row["consent"] == "granted" and row["browser"] == "chrome" and row["would_run"] is True
        assert spy.calls == []
        assert "consent granted (chrome)" in doctor.render_text(report)

    def ___LONG_STRING___(self, spy):
        row = next(r for r in doctor.build_report({})["sources"]["reddit"]["paths"] if r["path"] == "session")
        assert row["consent"] == "unset" and "setup --reddit-session" in row["action"]


def _cli(argv, config, environ=None):
    out, err = io.StringIO(), io.StringIO()
    with mock.patch.object(cli.env, "get_config", return_value=dict(config)), \
            mock.patch.dict(os.environ, {"LAST30DAYS_SKIP_PREFLIGHT": "1", **(environ or {})}), \
            mock.patch.object(sys, "argv", ["last30days.py", *argv]), \
            mock.patch.object(cli.pipeline, "run", side_effect=AssertionError("must not run")), \
            redirect_stdout(out), redirect_stderr(err):
        rc = cli.main()
    return rc, out.getvalue(), err.getvalue()


class TestCli:
    SESSION_ON = {"_BROWSER_COOKIE_MODE": "read", env.REDDIT_CONSENT_VAR: "true", env.REDDIT_FROM_BROWSER_VAR: "chrome"}

    def ___LONG_STRING___(self, tmp_path):
        rc, _out, err = _cli(["Ghostty terminal", "--record-fixtures", str(tmp_path / "rec")], self.SESSION_ON)
        assert rc == 2
        assert "--record-fixtures refuses" in err and "--no-browser-cookies" in err

    def ___LONG_STRING___(self, spy):
        with mock.patch.object(cli.env, "read_secret_env", return_value="hosted-test-key"), \
                mock.patch("lib.hosted.run_hosted", return_value=0):
            rc, _out, err = _cli(["Ghostty terminal"], self.SESSION_ON,
                                 environ={"LAST30DAYS_API_BASE": "https://hosted.example.test"})
        assert rc == 0
        assert "Reddit session is not used with the hosted backend" in err
        assert spy.calls == []
