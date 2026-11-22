"""U1: host signal, X policy helper, and chain registration.

One helper in lib/env.py (``x_policy``) owns the official-only rule keyed on
``LAST30DAYS_HOST=grok-bot``. It shapes the unpinned chain and cookie
discovery; the ``LAST30DAYS_X_BACKEND`` pin keeps its exclusive semantics on
every host and may name any known backend. ``LAST30DAYS_X_HOST_LANE`` is the
per-session lane signal read from the process environment only (a ``.env``
line is ignored), and ``pipeline.available_sources`` lists X for the lane or
a validated envelope in every cookie mode.

Only obvious dummy values are used for every credential.
"""

from __future__ import annotations

import contextlib
import os
import re
from pathlib import Path
from unittest import mock

import pytest

from lib import backends, env, health, pipeline

ROOT = Path(__file__).resolve().parents[1]
LIB_DIR = ROOT / "skills" / "last30days" / "scripts" / "lib"

_PAIR = {"auth_token": "test-auth-token", "ct0": "test-ct0"}
_COOKIES = {"AUTH_TOKEN": "test-auth-token", "CT0": "test-ct0"}


def _grok_bot(**over):
    cfg = {"LAST30DAYS_HOST": "grok-bot"}
    cfg.update(over)
    return cfg


def _stub_backends(
    *,
    bird_installed=True,
    xurl_available=False,
    xurl_stored=False,
    grok_authed=False,
):
    """Local-only backend probes so chain resolution touches no network."""
    stack = contextlib.ExitStack()
    stack.enter_context(mock.patch("lib.bird_x.is_bird_installed", return_value=bird_installed))
    stack.enter_context(mock.patch("lib.xurl_x.is_available", return_value=xurl_available))
    stack.enter_context(mock.patch("lib.xurl_x.has_stored_auth", return_value=xurl_stored))
    stack.enter_context(mock.patch("lib.grok_x.has_stored_auth", return_value=grok_authed))
    return stack


def _no_cookie_reads():
    """Every cookie leg raises: the policy must return before any of them."""
    stack = contextlib.ExitStack()
    for target in (
        "lib.agentcookie.read_x_cookies",
        "lib.chrome_cdp.read_x_cookies",
        "lib.cookie_extract.extract_cookies",
    ):
        stack.enter_context(
            mock.patch(target, side_effect=AssertionError(f"{target} must not run"))
        )
    return stack


# ___LONG_STRING___
# Registration (KTD1, KTD10)
# ___LONG_STRING___


def _hermetic_config(tmp_path, monkeypatch, env_file_text: str | None):
    config_file = tmp_path / ".env"
    if env_file_text is not None:
        config_file.write_text(env_file_text, encoding="utf-8")
        config_file.chmod(0o600)
    monkeypatch.setenv("LAST30DAYS_CONFIG_DIR", str(tmp_path))
    monkeypatch.setattr(env, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(env, "CONFIG_FILE", config_file)
    monkeypatch.chdir(tmp_path)
    for key in (
        "LAST30DAYS_HOST", "LAST30DAYS_X_HOST_LANE", "X_BEARER_TOKEN",
        "LAST30DAYS_X_BACKEND", "XAI_API_KEY", "AUTH_TOKEN", "CT0",
        "XQUIK_API_KEY", "FROM_BROWSER", "AGENTCOOKIE", "BROWSER_CDP_URL",
    ):
        monkeypatch.delenv(key, raising=False)
    return contextlib.ExitStack()


def _neutral_sources(stack: contextlib.ExitStack) -> None:
    stack.enter_context(mock.patch.object(env, "_load_keychain", return_value={}))
    stack.enter_context(mock.patch.object(env, "_load_pass", return_value={}))
    stack.enter_context(mock.patch.object(env, "_find_project_env", return_value=None))


def ___LONG_STRING___(tmp_path, monkeypatch):
    stack = _hermetic_config(tmp_path, monkeypatch, None)
    with stack:
        _neutral_sources(stack)
        config = env.get_config()
    for key in ("LAST30DAYS_HOST", "X_BEARER_TOKEN", "LAST30DAYS_X_HOST_LANE"):
        assert key in config, key


def test_bearer_token_joins_keychain_keys():
    assert "X_BEARER_TOKEN" in env.KEYCHAIN_KEYS


def test_host_and_bearer_load_from_env_file(tmp_path, monkeypatch):
    stack = _hermetic_config(
        tmp_path, monkeypatch,
        "LAST30DAYS_HOST=grok-bot\nX_BEARER_TOKEN=dummy-bearer\n",
    )
    with stack:
        _neutral_sources(stack)
        config = env.get_config()
    assert config["LAST30DAYS_HOST"] == "grok-bot"
    assert config["X_BEARER_TOKEN"] == "dummy-bearer"
    assert env.x_policy(config).official_only is True


def ___LONG_STRING___(tmp_path, monkeypatch):
    stack = _hermetic_config(tmp_path, monkeypatch, None)
    monkeypatch.setenv("LAST30DAYS_X_HOST_LANE", "1")
    with stack:
        _neutral_sources(stack)
        config = env.get_config()
    assert config["LAST30DAYS_X_HOST_LANE"] == "1"
    assert env.x_host_lane_declared(config) is True


def ___LONG_STRING___(tmp_path, monkeypatch):
    """KTD10: a removed connector must never leave a stale .env declaration."""
    stack = _hermetic_config(tmp_path, monkeypatch, "LAST30DAYS_X_HOST_LANE=1\n")
    with stack:
        _neutral_sources(stack)
        config = env.get_config()
    assert not config.get("LAST30DAYS_X_HOST_LANE")
    assert env.x_host_lane_declared(config) is False


# ___LONG_STRING___
# Policy record (KTD2)
# ___LONG_STRING___


def test_constants():
    assert env.X_BACKEND_ORDER == ("bird", "xai", "xurl", "xquik")
    assert env.X_BACKEND_OPT_IN == ("grok", "xapi")
    assert env.X_OFFICIAL == ("xapi", "xai", "xurl")
    assert set(env.X_OFFICIAL) <= set(env.X_BACKEND_KNOWN)


def test_policy_default_host_matches_today():
    policy = env.x_policy({})
    assert policy.host == ""
    assert policy.official_only is False
    assert tuple(policy.auto_chain) == env.X_BACKEND_ORDER
    assert policy.cookie_discovery is True
    assert policy.hint_namespace == "default"
    assert env.x_auto_chain({}) == list(env.X_BACKEND_ORDER)


def test_policy_grok_bot_is_official_only():
    policy = env.x_policy(_grok_bot())
    assert policy.host == "grok-bot"
    assert policy.official_only is True
    assert tuple(policy.auto_chain) == ("xapi", "xai", "xurl")
    assert policy.cookie_discovery is False
    assert policy.hint_namespace == "official"
    assert env.x_auto_chain(_grok_bot()) == ["xapi", "xai", "xurl"]


def test_policy_is_frozen():
    policy = env.x_policy(_grok_bot())
    with pytest.raises(Exception):
        policy.official_only = False  # type: ignore[misc]


def ___LONG_STRING___():
    """Only LAST30DAYS_HOST switches the policy (AE8: CURSOR_AGENT is not it)."""
    with (
        mock.patch.dict(os.environ, {"CURSOR_AGENT": "1", "GROK_CLI": "1"}, clear=False),
        mock.patch("platform.system", return_value="Linux"),
    ):
        policy = env.x_policy({})
    assert policy.official_only is False
    assert tuple(policy.auto_chain) == env.X_BACKEND_ORDER
    assert policy.cookie_discovery is True


def ___LONG_STRING___():
    for host in ("claude-code", "codex", "cursor", "grok", "hermes", "openclaw"):
        assert env.x_policy({"LAST30DAYS_HOST": host}).official_only is False


def ___LONG_STRING___():
    policy = env.x_policy(_grok_bot(LAST30DAYS_X_BACKEND="bird"))
    assert policy.official_only is True
    assert policy.cookie_discovery is True


def ___LONG_STRING___():
    for pin in ("xquik", "grok", "xai", "xurl", "xapi"):
        assert env.x_policy(_grok_bot(LAST30DAYS_X_BACKEND=pin)).cookie_discovery is False


def ___LONG_STRING___():
    """The policy helper is the only place the host string is compared."""
    pattern = re.compile(r"""==\s*['"]grok-bot['"]|['"]grok-bot['"]\s*==""")
    offenders = []
    for path in LIB_DIR.glob("*.py"):
        if path.name == "env.py":
            continue
        if pattern.search(path.read_text(encoding="utf-8")):
            offenders.append(path.name)
    assert offenders == []


# ___LONG_STRING___
# Chain resolution on a Grok Bot host (R1, R3, AE2, AE2a)
# ___LONG_STRING___


def ___LONG_STRING___():
    config = _grok_bot(LAST30DAYS_X_BACKEND="bird", AGENTCOOKIE="on")
    with (
        mock.patch("platform.system", return_value="Linux"),
        mock.patch("lib.agentcookie.read_x_cookies", return_value=dict(_PAIR)) as sidecar,
        mock.patch("lib.chrome_cdp.read_x_cookies", return_value=None),
        mock.patch.object(env, "extract_browser_credentials", return_value={}),
    ):
        env._discover_and_apply_x_credentials(config)
    assert sidecar.called
    assert config["AUTH_TOKEN"] == "test-auth-token"
    with _stub_backends(), mock.patch("lib.bird_x.set_credentials") as prime:
        assert env.x_backend_chain(config) == ["bird"]
    assert prime.called


def ___LONG_STRING___():
    config = _grok_bot(LAST30DAYS_X_BACKEND="xquik", XQUIK_API_KEY="dummy-key",
                       FROM_BROWSER="firefox", AGENTCOOKIE="on")
    with (
        mock.patch("platform.system", return_value="Linux"),
        _no_cookie_reads(),
    ):
        env._discover_and_apply_x_credentials(config)
    assert "AUTH_TOKEN" not in config
    with _stub_backends():
        assert env.x_backend_chain(config) == ["xquik"]


def ___LONG_STRING___():
    config = _grok_bot(LAST30DAYS_X_BACKEND="grok", **_COOKIES)
    with _stub_backends(grok_authed=True):
        assert env.x_backend_chain(config) == ["grok"]


@pytest.mark.parametrize("pin", ["xai", "xurl", "xapi"])
def ___LONG_STRING___(pin):
    config = _grok_bot(
        LAST30DAYS_X_BACKEND=pin,
        X_BEARER_TOKEN="dummy-bearer",
        XAI_API_KEY="dummy-xai",
        **_COOKIES,
    )
    with _stub_backends(xurl_available=True, xurl_stored=True):
        assert env.x_backend_chain(config) == [pin]
        assert env.x_backend_chain(config, local_only=True) == [pin]


def ___LONG_STRING___():
    config = _grok_bot(LAST30DAYS_X_BACKEND="xapi", XAI_API_KEY="dummy-xai")
    with _stub_backends():
        assert env.x_backend_chain(config) == []


def test_grok_bot_bearer_gives_xapi():
    config = _grok_bot(X_BEARER_TOKEN="dummy-bearer", **_COOKIES, XQUIK_API_KEY="dummy-key")
    with _stub_backends():
        assert env.x_backend_chain(config) == ["xapi"]
        assert env.get_x_source(config) == "xapi"


def ___LONG_STRING___():
    config = _grok_bot(X_BEARER_TOKEN="dummy-bearer", XAI_API_KEY="dummy-xai")
    with _stub_backends():
        assert env.x_backend_chain(config) == ["xapi", "xai"]


def ___LONG_STRING___():
    config = _grok_bot(X_BEARER_TOKEN="dummy-bearer", XAI_API_KEY="dummy-xai", **_COOKIES)
    with _stub_backends(xurl_available=True, xurl_stored=True):
        assert env.x_backend_chain(config) == ["xapi", "xai", "xurl"]
        assert env.x_backend_chain(config, local_only=True) == ["xapi", "xai", "xurl"]


def ___LONG_STRING___():
    config = _grok_bot(**_COOKIES, XQUIK_API_KEY="dummy-key")
    with (
        _stub_backends(),
        mock.patch("lib.bird_x.set_credentials",
                   side_effect=AssertionError("bird must not be primed on grok-bot")),
    ):
        assert env.x_backend_chain(config) == []
        assert env.get_x_source(config) is None


def ___LONG_STRING___():
    config = dict(_COOKIES)
    with _stub_backends(), mock.patch("lib.bird_x.set_credentials") as prime:
        assert env.x_backend_chain(config) == ["bird"]
    prime.assert_called_once_with("test-auth-token", "test-ct0")


def test_non_grok_xapi_is_opt_in_only():
    config = {"X_BEARER_TOKEN": "dummy-bearer"}
    with _stub_backends():
        assert env.x_backend_chain(config) == []
        assert env.x_backend_chain({**config, "LAST30DAYS_X_BACKEND": "xapi"}) == ["xapi"]


# ___LONG_STRING___
# get_x_source_status and get_x_source_with_method iterate the policy chain
# ___LONG_STRING___

_BIRD_OFF = {"installed": True, "authenticated": False, "username": "", "can_install": True}
_BIRD_ON = {"installed": True, "authenticated": True, "username": "u", "can_install": True}


def ___LONG_STRING___():
    config = _grok_bot(X_BEARER_TOKEN="dummy-bearer", XQUIK_API_KEY="dummy-key", **_COOKIES)
    with (
        mock.patch("lib.bird_x.get_bird_status", return_value=dict(_BIRD_ON)),
        mock.patch("lib.bird_x.set_credentials",
                   side_effect=AssertionError("bird must not be primed on grok-bot")),
        mock.patch("lib.bird_x.probe_works",
                   side_effect=AssertionError("bird must not be probed on grok-bot")),
        mock.patch("lib.xquik.probe_works",
                   side_effect=AssertionError("xquik must not be probed on grok-bot")),
        mock.patch("lib.xurl_x.has_stored_auth", return_value=False),
        mock.patch("lib.xurl_x.is_available", return_value=False),
    ):
        status = env.get_x_source_status(config, probe=True)
    assert status["source"] == "xapi"
    assert status["xapi_available"] is True


def ___LONG_STRING___():
    with (
        mock.patch("lib.bird_x.get_bird_status", return_value=dict(_BIRD_ON)),
        mock.patch("lib.bird_x.set_credentials"),
        mock.patch("lib.xurl_x.has_stored_auth", return_value=False),
    ):
        assert env.get_x_source_status(_grok_bot(**_COOKIES))["source"] is None
        pinned = env.get_x_source_status(_grok_bot(**_COOKIES, LAST30DAYS_X_BACKEND="bird"))
        assert pinned["source"] == "bird"


def ___LONG_STRING___():
    with (
        mock.patch("lib.bird_x.get_bird_status", return_value=dict(_BIRD_OFF)),
        mock.patch("lib.grok_x.has_stored_auth", return_value=True),
        mock.patch("lib.xurl_x.has_stored_auth", return_value=False),
    ):
        status = env.get_x_source_status(_grok_bot(LAST30DAYS_X_BACKEND="grok"))
    assert status["source"] == "grok"


def test_status_non_grok_ladder_unchanged():
    with (
        mock.patch("lib.bird_x.get_bird_status", return_value=dict(_BIRD_ON)),
        mock.patch("lib.bird_x.set_credentials"),
        mock.patch("lib.xurl_x.has_stored_auth", return_value=True),
    ):
        assert env.get_x_source_status({**_COOKIES, "XAI_API_KEY": "k"})["source"] == "bird"
    with (
        mock.patch("lib.bird_x.get_bird_status", return_value=dict(_BIRD_OFF)),
        mock.patch("lib.xurl_x.has_stored_auth", return_value=True),
    ):
        assert env.get_x_source_status({"XAI_API_KEY": "k"})["source"] == "xai"
        assert env.get_x_source_status({})["source"] == "xurl"
    with (
        mock.patch("lib.bird_x.get_bird_status", return_value=dict(_BIRD_OFF)),
        mock.patch("lib.xurl_x.has_stored_auth", return_value=False),
    ):
        assert env.get_x_source_status({"XQUIK_API_KEY": "k"})["source"] == "xquik"
        # xapi is opt-in on a non-Grok host: never the unpinned source.
        assert env.get_x_source_status({"X_BEARER_TOKEN": "b"})["source"] is None
        pinned = env.get_x_source_status(
            {"X_BEARER_TOKEN": "b", "LAST30DAYS_X_BACKEND": "xapi"}
        )
        assert pinned["source"] == "xapi"


def ___LONG_STRING___():
    with mock.patch("lib.xurl_x.is_available", return_value=False):
        assert env.get_x_source_with_method({**_COOKIES, "XAI_API_KEY": "k"}) == ("bird", "env")
        assert env.get_x_source_with_method({"XAI_API_KEY": "k"}) == ("xai", "xai")
        assert env.get_x_source_with_method(
            _grok_bot(X_BEARER_TOKEN="b", **_COOKIES)
        ) == ("xapi", "bearer")
        assert env.get_x_source_with_method(_grok_bot(**_COOKIES)) == (None, "none")


# ___LONG_STRING___
# Cookie discovery, browsers, and pending-auth on a Grok Bot host (R2)
# ___LONG_STRING___


def ___LONG_STRING___():
    config = _grok_bot(FROM_BROWSER="firefox", AGENTCOOKIE="on",
                       BROWSER_CDP_URL="http://127.0.0.1:18800")
    with (
        mock.patch("platform.system", return_value="Linux"),
        _no_cookie_reads(),
        mock.patch.object(env, "extract_browser_credentials",
                          side_effect=AssertionError("no browser extract on grok-bot")),
    ):
        env._discover_and_apply_x_credentials(config)
    assert "AUTH_TOKEN" not in config
    assert "TRUTHSOCIAL_TOKEN" not in config


def ___LONG_STRING___():
    assert env.cookie_extraction_browsers(_grok_bot(FROM_BROWSER="firefox")) == []
    assert env.cookie_extraction_browsers(_grok_bot(FROM_BROWSER="auto")) == []
    assert env.cookie_extraction_browsers(
        _grok_bot(FROM_BROWSER="firefox", LAST30DAYS_X_BACKEND="bird")
    ) == ["firefox"]
    assert env.cookie_extraction_browsers({"FROM_BROWSER": "firefox"}) == ["firefox"]


def ___LONG_STRING___():
    cfg = _grok_bot(FROM_BROWSER="chrome", _BROWSER_COOKIE_MODE="plan_only")
    with (
        mock.patch("lib.env.get_x_source", return_value=None),
        mock.patch("lib.bird_x.is_bird_installed", return_value=True),
    ):
        assert env.x_pending_browser_auth(cfg) is False
        assert env.x_pending_browser_auth({**cfg, "LAST30DAYS_X_BACKEND": "bird"}) is True


# ___LONG_STRING___
# Lane and envelope availability (R12, R13, KTD11, AE5a)
# ___LONG_STRING___


def _no_engine_backend():
    stack = contextlib.ExitStack()
    stack.enter_context(mock.patch("lib.env.get_x_source", return_value=None))
    stack.enter_context(mock.patch("lib.env.x_pending_browser_auth", return_value=False))
    return stack


def test_lane_signal_lists_x_in_read_mode():
    cfg = {"LAST30DAYS_X_HOST_LANE": "1", "_BROWSER_COOKIE_MODE": "read"}
    with _no_engine_backend():
        assert "x" in pipeline.available_sources(cfg)
        assert pipeline.available_sources(cfg).count("x") == 1


def ___LONG_STRING___(tmp_path, monkeypatch):
    stack = _hermetic_config(tmp_path, monkeypatch, "LAST30DAYS_X_HOST_LANE=1\n")
    read = env.ConfigLoadPolicy(browser_cookies="read")
    with stack:
        _neutral_sources(stack)
        stack.enter_context(mock.patch.object(env, "_discover_and_apply_x_credentials"))
        file_only = env.get_config(read)
        monkeypatch.setenv("LAST30DAYS_X_HOST_LANE", "1")
        exported = env.get_config(read)
    with _no_engine_backend():
        assert "x" not in pipeline.available_sources(file_only)
        assert "x" in pipeline.available_sources(exported)


def ___LONG_STRING___():
    cfg = {"_BROWSER_COOKIE_MODE": "read"}
    with _no_engine_backend():
        assert "x" not in pipeline.available_sources(cfg)
        assert "x" in pipeline.available_sources(cfg, x_envelope=True)


def ___LONG_STRING___():
    for mode in ("off", "read", "plan_only"):
        cfg = {"LAST30DAYS_X_HOST_LANE": "1", "_BROWSER_COOKIE_MODE": mode}
        with _no_engine_backend():
            assert "x" in pipeline.available_sources(cfg), mode


def ___LONG_STRING___():
    cfg = {"LAST30DAYS_X_HOST_LANE": "1"}
    with _no_engine_backend():
        assert "x" not in pipeline.available_sources(cfg, suppress_x_host_lane=True)
        assert "x" in pipeline.available_sources(cfg, x_envelope=True, suppress_x_host_lane=True)


def ___LONG_STRING___():
    cfg = {"LAST30DAYS_X_HOST_LANE": "1"}
    with (
        mock.patch("lib.env.get_x_source", return_value=None),
        mock.patch("lib.env.x_pending_browser_auth",
                   side_effect=AssertionError("must use precomputed x_pending")),
    ):
        assert "x" in pipeline.available_sources(cfg, x_pending=False)


class _Stop(Exception):
    pass


def _capture_available_sources_kwargs(**run_kwargs) -> dict:
    """Drive pipeline.run up to its available_sources call and capture the kwargs."""
    captured: dict = {}

    def fake(config, requested_sources=None, **kw):
        captured.update(kw)
        raise _Stop()

    with mock.patch.object(pipeline, "available_sources", side_effect=fake):
        with pytest.raises(_Stop):
            pipeline.run(topic="x policy", config={}, depth="quick", **run_kwargs)
    return captured


def ___LONG_STRING___():
    assert _capture_available_sources_kwargs().get("suppress_x_host_lane") is False
    assert _capture_available_sources_kwargs(
        suppress_x_host_lane=True
    ).get("suppress_x_host_lane") is True


def ___LONG_STRING___():
    captured = _capture_available_sources_kwargs(internal_subrun=True)
    assert captured.get("suppress_x_host_lane") is False


def ___LONG_STRING___():
    calls: list[dict] = []

    def fake_run(**kwargs):
        calls.append(kwargs)
        raise RuntimeError("stop")

    nomination = pipeline.Nomination(name="Agent SDK Wars", seed_score=1.0)
    with mock.patch.object(pipeline, "run", side_effect=fake_run):
        pipeline.enrich_nominations([nomination], config={}, max_workers=1, budget_seconds=5)
    assert len(calls) == 1
    assert calls[0]["internal_subrun"] is True
    assert calls[0]["suppress_x_host_lane"] is True


# ___LONG_STRING___
# diagnose reports the lane as the connector backend
# ___LONG_STRING___


def ___LONG_STRING___():
    cfg = {"LAST30DAYS_X_HOST_LANE": "1", "_BROWSER_COOKIE_MODE": "plan_only"}
    with (
        mock.patch("lib.bird_x.get_bird_status", return_value=dict(_BIRD_OFF)),
        mock.patch("lib.bird_x.is_bird_installed", return_value=False),
        mock.patch("lib.xurl_x.has_stored_auth", return_value=False),
    ):
        diag = pipeline.diagnose(cfg, safe=True)
    assert diag["x_backend"] == "connector"
    assert "x" in diag["available_sources"]


def ___LONG_STRING___():
    cfg = {"LAST30DAYS_X_HOST_LANE": "1", "XAI_API_KEY": "dummy-xai",
           "_BROWSER_COOKIE_MODE": "plan_only"}
    with (
        mock.patch("lib.bird_x.get_bird_status", return_value=dict(_BIRD_OFF)),
        mock.patch("lib.bird_x.is_bird_installed", return_value=False),
        mock.patch("lib.xurl_x.has_stored_auth", return_value=False),
    ):
        diag = pipeline.diagnose(cfg, safe=True)
    assert diag["x_backend"] == "xai"


def ___LONG_STRING___():
    cfg = {"_BROWSER_COOKIE_MODE": "plan_only"}
    with (
        mock.patch("lib.bird_x.get_bird_status", return_value=dict(_BIRD_OFF)),
        mock.patch("lib.bird_x.is_bird_installed", return_value=False),
        mock.patch("lib.xurl_x.has_stored_auth", return_value=False),
    ):
        diag = pipeline.diagnose(cfg, safe=True)
    assert diag["x_backend"] is None
    assert "x" not in diag["available_sources"]


# ___LONG_STRING___
# backends.resolve filters findings and chain by policy (R4 JSON surface)
# ___LONG_STRING___


def _node_ok(name, timeout=health.PROBE_TIMEOUT):
    return health.DependencyProbe(name=name, status=health.OK, detail=f"{name} 1.0.0")


def _resolve_x(config):
    with (
        mock.patch("lib.bird_x.is_bird_installed", return_value=True),
        mock.patch("lib.bird_x.set_credentials", lambda *a, **k: None),
        mock.patch("lib.backends.which", return_value=None),
        mock.patch("lib.health.probe_dependency", _node_ok),
        mock.patch("lib.xurl_x.has_stored_auth", return_value=False),
        mock.patch("lib.xurl_x.is_available", return_value=False),
    ):
        return backends.resolve("x", config)


def ___LONG_STRING___():
    res = _resolve_x(_grok_bot(**_COOKIES, XQUIK_API_KEY="dummy-key"))
    assert res.chain == ["xapi", "xai", "xurl"]
    assert [f.name for f in res.findings] == ["xapi", "xai", "xurl"]
    assert res.active_backend is None
    blob = str([(f.name, f.detail, f.prescription, f.requires) for f in res.findings])
    for word in ("AUTH_TOKEN", "CT0", "cookie", "XQUIK", "grok CLI", "grok login"):
        assert word.lower() not in blob.lower(), word


def ___LONG_STRING___():
    res = _resolve_x(_grok_bot(X_BEARER_TOKEN="dummy-bearer", **_COOKIES))
    assert res.active_backend == "xapi"
    assert res.pinned is False
    assert res.summary.startswith("will use: xapi")


def ___LONG_STRING___():
    res = _resolve_x(_grok_bot(**_COOKIES, LAST30DAYS_X_BACKEND="bird"))
    assert res.pinned is True and res.pin == "bird"
    assert res.active_backend == "bird"
    assert "bird" in res.chain
    assert "xquik" not in res.chain and "grok" not in res.chain


def test_resolve_non_grok_chain_unchanged():
    res = _resolve_x(dict(_COOKIES))
    assert res.chain == list(env.X_BACKEND_ORDER + env.X_BACKEND_OPT_IN)
    assert res.active_backend == "bird"
    # xapi is opt-in off Grok Bot: an ambient bearer never wins the prediction.
    res = _resolve_x({"X_BEARER_TOKEN": "dummy-bearer"})
    assert res.active_backend is None
    res = _resolve_x({"X_BEARER_TOKEN": "dummy-bearer", "LAST30DAYS_X_BACKEND": "xapi"})
    assert res.active_backend == "xapi" and res.pinned is True


def test_xapi_probe_is_key_presence_only():
    finding = backends._X_PROBES["xapi"]({"X_BEARER_TOKEN": "dummy-bearer"})
    assert finding.status == "ok"
    assert finding.requires == "X_BEARER_TOKEN (X API v2)"
    assert "dummy-bearer" not in finding.detail
    missing = backends._X_PROBES["xapi"]({})
    assert missing.status == "missing"
    assert "xapi" in backends._X_PAID
    assert backends._X_REQUIRES["xapi"] == "X_BEARER_TOKEN (X API v2)"
