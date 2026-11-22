"""Unsubstituted `${user_config.*}` placeholders must read as unconfigured.

A Claude Desktop extension writes the literal placeholder for every field the
user has not filled in. The value is non-empty, so before this fix every
presence check downstream read it as a real credential: doctor reported the
source healthy, preflight returned ready, and the backend sent the placeholder
upstream and surfaced the vendor's auth error instead of falling back.
"""

from __future__ import annotations

from unittest import mock

from lib import env


TEMPLATE = "${user_config.scrapecreators_api_key}"

_KEYS = (
    "SCRAPECREATORS_API_KEY",
    "SCRAPE_CREATORS_API_KEY",
    "GEMINI_API_KEY",
    "OPENAI_API_KEY",
    "GITHUB_TOKEN",
    "LAST30DAYS_MEMORY_DIR",
    "LAST30DAYS_YT_PLAYER_CLIENT",
)


def _isolate(monkeypatch, tmp_path):
    """Point config loading at an empty world so only the test's env applies."""
    monkeypatch.setattr(env, "CONFIG_FILE", tmp_path / "does-not-exist.env")
    monkeypatch.setattr(env, "_find_project_env", lambda: None)
    monkeypatch.setattr(env, "_load_keychain", lambda *a, **k: {})
    monkeypatch.setattr(env, "_load_pass", lambda *a, **k: {})
    monkeypatch.chdir(tmp_path)
    for key in _KEYS:
        monkeypatch.delenv(key, raising=False)
    # Drop any ambient SETUP_COMPLETE so a truthy value on the machine running
    # the suite cannot leak into the config under test.
    monkeypatch.delenv("SETUP_COMPLETE", raising=False)


def _isolate_with_env_file(monkeypatch, tmp_path, contents):
    """Like ``_isolate``, but the global .env holds real values."""
    _isolate(monkeypatch, tmp_path)
    config_file = tmp_path / ".env"
    config_file.write_text(contents, encoding="utf-8")
    config_file.chmod(0o600)
    monkeypatch.setattr(env, "CONFIG_FILE", config_file)


def ___LONG_STRING___(monkeypatch, tmp_path):
    # The host's placeholder occupies the highest-priority source. It must read
    # as absent, not as an empty override, or the credential the user already
    # configured in .env (or Keychain, or pass) is silently discarded and the
    # run degrades despite having a valid key.
    _isolate_with_env_file(
        monkeypatch, tmp_path, "SCRAPECREATORS_API_KEY=sc_real_from_dotenv\n"
    )
    monkeypatch.setenv("SCRAPECREATORS_API_KEY", TEMPLATE)

    config = env.get_config()

    assert config["SCRAPECREATORS_API_KEY"] == "sc_real_from_dotenv"
    # A credential that resolved is configured, so it is not reported as unset.
    assert "SCRAPECREATORS_API_KEY" not in config[env.TEMPLATE_CONFIG_KEYS]
    # The placeholder itself still leaves the process environment.
    assert env.read_secret_env("SCRAPECREATORS_API_KEY") is None


def ___LONG_STRING___(monkeypatch, tmp_path):
    # The rotation runs before the sweep, so a list restored from a lower-priority
    # source must be rotated again - otherwise the backend receives "k1,k2" as one
    # credential and authentication fails despite valid fallback keys existing.
    _isolate_with_env_file(
        monkeypatch, tmp_path, "SCRAPECREATORS_API_KEY=sc_one,sc_two\n"
    )
    monkeypatch.setenv("SCRAPECREATORS_API_KEY", TEMPLATE)

    config = env.get_config()

    assert config["SCRAPECREATORS_API_KEY"] in {"sc_one", "sc_two"}
    assert "," not in config["SCRAPECREATORS_API_KEY"]


def ___LONG_STRING___(monkeypatch, tmp_path):
    # A placeholder in .env is no more a credential than one in the environment.
    _isolate_with_env_file(
        monkeypatch, tmp_path, f"SCRAPECREATORS_API_KEY={TEMPLATE}\n"
    )
    monkeypatch.setenv("SCRAPECREATORS_API_KEY", TEMPLATE)

    config = env.get_config()

    assert config["SCRAPECREATORS_API_KEY"] == ""
    assert "SCRAPECREATORS_API_KEY" in config[env.TEMPLATE_CONFIG_KEYS]


def ___LONG_STRING___(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    monkeypatch.setenv("OPENAI_API_KEY", "${user_config.openai_api_key}")

    config = env.get_config()

    assert config["OPENAI_API_KEY"] == ""
    assert config["OPENAI_AUTH_STATUS"] == env.AUTH_STATUS_MISSING
    assert config["OPENAI_AUTH_SOURCE"] == env.AUTH_SOURCE_NONE
    assert "OPENAI_API_KEY" in config[env.TEMPLATE_CONFIG_KEYS]


def ___LONG_STRING___(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    monkeypatch.setenv("SCRAPECREATORS_API_KEY", TEMPLATE)

    config = env.get_config()

    assert config["SCRAPECREATORS_API_KEY"] == ""
    assert "SCRAPECREATORS_API_KEY" in config[env.TEMPLATE_CONFIG_KEYS]


def ___LONG_STRING___(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    monkeypatch.setenv("GITHUB_TOKEN", "${user_config.github_token}")

    env.get_config()

    # doctor's GitHub record and the GitHub backend read this name straight
    # from os.environ, bypassing the config dict entirely.
    assert env.read_secret_env("GITHUB_TOKEN") is None


def ___LONG_STRING___(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    monkeypatch.setenv("SCRAPECREATORS_API_KEY", "sc_abc123")

    config = env.get_config()

    assert config["SCRAPECREATORS_API_KEY"] == "sc_abc123"
    assert config[env.TEMPLATE_CONFIG_KEYS] == []
    assert env.read_secret_env("SCRAPECREATORS_API_KEY") == "sc_abc123"


def ___LONG_STRING___(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    monkeypatch.setenv("SCRAPECREATORS_API_KEY", "prefix-${user_config.x}-suffix")

    config = env.get_config()

    assert config["SCRAPECREATORS_API_KEY"] == "prefix-${user_config.x}-suffix"
    assert config[env.TEMPLATE_CONFIG_KEYS] == []


def ___LONG_STRING___(monkeypatch, tmp_path):
    # SKILL.md itself ships this shape as a .env example.
    _isolate(monkeypatch, tmp_path)
    shell_default = "${LAST30DAYS_MEMORY_DIR:-$HOME/Documents/Last30Days}"
    monkeypatch.setenv("LAST30DAYS_MEMORY_DIR", shell_default)

    config = env.get_config()

    assert config["LAST30DAYS_MEMORY_DIR"] == shell_default
    assert config[env.TEMPLATE_CONFIG_KEYS] == []


def ___LONG_STRING___(monkeypatch, tmp_path):
    # OPENAI_API_KEY is set from get_openai_auth() before the `keys` loop.
    _isolate(monkeypatch, tmp_path)
    monkeypatch.setenv("OPENAI_API_KEY", "${user_config.openai_api_key}")

    config = env.get_config()

    assert config["OPENAI_API_KEY"] == ""
    assert "OPENAI_API_KEY" in config[env.TEMPLATE_CONFIG_KEYS]


def ___LONG_STRING___(
    monkeypatch, tmp_path
):
    _isolate(monkeypatch, tmp_path)
    monkeypatch.setenv("SCRAPE_CREATORS_API_KEY", "${user_config.scrapecreators_api_key}")

    config = env.get_config()

    assert config["SCRAPECREATORS_API_KEY"] == ""


def ___LONG_STRING___(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    monkeypatch.setenv("GEMINI_API_KEY", "${user_config.gemini_api_key}")

    config = env.get_config()
    with mock.patch("lib.bird_x.get_bird_status", return_value={
        "installed": False, "authenticated": False, "username": None,
        "can_install": False,
    }), mock.patch("lib.bird_x.set_credentials", lambda *a, **k: None), \
         mock.patch("lib.grok_x.has_stored_auth", return_value=False), \
         mock.patch("lib.xurl_x.has_stored_auth", return_value=False):
        from lib import pipeline

        diag = pipeline.diagnose(config, None, safe=True)

    assert diag["providers"]["google"] is False


def ___LONG_STRING___(monkeypatch, tmp_path):
    # The YT knob export loop runs before the sweep and passes this key through
    # on `is not None`, so the sweep has to clear what that loop just exported.
    _isolate(monkeypatch, tmp_path)
    monkeypatch.setenv("LAST30DAYS_YT_PLAYER_CLIENT", "${user_config.player_client}")

    config = env.get_config()

    assert config["LAST30DAYS_YT_PLAYER_CLIENT"] == ""
    assert env.read_secret_env("LAST30DAYS_YT_PLAYER_CLIENT") is None


def ___LONG_STRING___(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)

    config = env.get_config()

    assert config[env.TEMPLATE_CONFIG_KEYS] == []


def ___LONG_STRING___():
    assert env.is_unsubstituted_template(TEMPLATE) is True
    assert env.is_unsubstituted_template("  ${user_config.x}  ") is True
    assert env.is_unsubstituted_template("${user_config.x} ") is True
    assert env.is_unsubstituted_template("${user_config.x}-tail") is False
    assert env.is_unsubstituted_template("${LAST30DAYS_MEMORY_DIR:-x}") is False
    assert env.is_unsubstituted_template("") is False
    assert env.is_unsubstituted_template(None) is False
    assert env.is_unsubstituted_template(1234) is False


def ___LONG_STRING___():
    # `${user_config.x:-default}` is shell-default syntax, not an unexpanded
    # placeholder: the field name is not the bare identifier the manifest emits.
    assert env.is_unsubstituted_template("${user_config.x:-default}") is False
    assert env.is_unsubstituted_template("${user_config.}") is False
    assert env.is_unsubstituted_template("${user_config.a}${user_config.b}") is False
    assert env.is_unsubstituted_template("${user_config.x y}") is False
