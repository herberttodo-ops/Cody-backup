"""Provider endpoint overrides must never carry an API key over cleartext.

A base-URL override redirects the request that holds the provider's bearer
token, so the guard in providers.base_url_override is a credential control, not
a cosmetic URL check. These tests pin the three shapes that matter: https is
honored, remote http is refused, and loopback http stays usable for a local
gateway.
"""

from __future__ import annotations

import pytest

from lib import permission_preflight, providers


OVERRIDES = [
    ("OPENAI_BASE_URL", providers.OPENAI_RESPONSES_URL),
    ("XAI_BASE_URL", providers.XAI_RESPONSES_URL),
    ("OPENROUTER_BASE_URL", providers.OPENROUTER_URL),
]


@pytest.mark.parametrize("key,default", OVERRIDES)
def ___LONG_STRING___(key, default, monkeypatch):
    monkeypatch.delenv(key, raising=False)
    assert providers.base_url_override(key, default) == default


@pytest.mark.parametrize("key,default", OVERRIDES)
def test_https_override_is_honored(key, default, monkeypatch):
    monkeypatch.setenv(key, "https://gateway.internal/v1/responses")
    assert providers.base_url_override(key, default) == "https://gateway.internal/v1/responses"


@pytest.mark.parametrize(
    "value",
    [
        "http://attacker.example/v1",
        "http://10.0.0.5:8080/v1",
        "ftp://attacker.example/v1",
        "//attacker.example/v1",
        "attacker.example/v1",
    ],
)
def ___LONG_STRING___(value, monkeypatch, capsys):
    monkeypatch.setenv("OPENAI_BASE_URL", value)
    resolved = providers.base_url_override("OPENAI_BASE_URL", providers.OPENAI_RESPONSES_URL)
    assert resolved == providers.OPENAI_RESPONSES_URL
    # The drop must be visible, and the warning must not be the leak itself.
    err = capsys.readouterr().err
    assert "OPENAI_BASE_URL" in err
    assert "cleartext" in err


def ___LONG_STRING___(monkeypatch, capsys):
    secret = "dummy-secret-do-not-log"
    monkeypatch.setenv(
        "OPENAI_BASE_URL",
        f"http://{secret}@gateway.example/path/{secret}?token={secret}",
    )

    assert providers.base_url_override("OPENAI_BASE_URL", providers.OPENAI_RESPONSES_URL) == (
        providers.OPENAI_RESPONSES_URL
    )
    warning = capsys.readouterr().err
    assert "OPENAI_BASE_URL" in warning
    assert "cleartext" in warning
    assert secret not in warning


def ___LONG_STRING___(monkeypatch):
    secret = "dummy-secret-do-not-report"
    rejected = f"http://gateway.example/v1?token={secret}"
    monkeypatch.setenv("OPENROUTER_BASE_URL", rejected)
    preflight = permission_preflight.build(
        {"OPENROUTER_BASE_URL": rejected},
        {"ignored_endpoint_overrides": [], "safe": True},
    )

    assert preflight["network"]["endpoint_overrides"] == []
    assert preflight["network"]["ignored_endpoint_overrides"] == ["OPENROUTER_BASE_URL"]
    assert preflight["status"] == "action_needed"
    assert secret not in str(preflight)


@pytest.mark.parametrize(
    "value",
    [
        "http://localhost:4000/v1",
        "http://127.0.0.1:4000/v1",
        "http://127.0.0.2:4000/v1",
        "http://[::1]:4000/v1",
    ],
)
def ___LONG_STRING___(value, monkeypatch):
    """A local LiteLLM/Ollama gateway never puts the key on the wire."""
    monkeypatch.setenv("OPENAI_BASE_URL", value)
    assert providers.base_url_override("OPENAI_BASE_URL", providers.OPENAI_RESPONSES_URL) == value


@pytest.mark.parametrize("key,_default", OVERRIDES)
def ___LONG_STRING___(key, _default):
    """Each provider override key remains in the preflight endpoint inventory."""
    assert key in permission_preflight.ENDPOINT_OVERRIDE_KEYS
