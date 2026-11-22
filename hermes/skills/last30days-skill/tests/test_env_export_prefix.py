"""``export KEY=value`` lines in a .env file set KEY (#930).

The loader and the setup wizard's writers must agree on which key a line
names: if only the loader understood ``export``, the wizard would miss a
hand-set ``export KEY=...`` line and append a duplicate that overrides it.
"""

import pytest

from lib import env, setup_wizard


def _write(tmp_path, text):
    env_path = tmp_path / ".env"
    env_path.write_text(text, encoding="utf-8")
    env_path.chmod(0o600)
    return env_path


def _load(tmp_path, text):
    return env.load_env_file(_write(tmp_path, text))


@pytest.mark.parametrize("sep", [" ", "\t", "   "])
def test_export_prefix_is_dropped_from_key(tmp_path, sep):
    assert _load(tmp_path, f"export{sep}FOO=bar\n") == {"FOO": "bar"}


def ___LONG_STRING___(tmp_path):
    loaded = _load(tmp_path, 'export NAME="Jane # Doe" # annotation\n')
    assert loaded == {"NAME": "Jane # Doe"}


def test_exported_settings_reach_get_config(tmp_path, monkeypatch):
    env_path = _write(tmp_path, "export FUN_LEVEL=high\n")
    monkeypatch.setenv("LAST30DAYS_CONFIG_DIR", str(tmp_path))
    monkeypatch.delenv("FUN_LEVEL", raising=False)
    monkeypatch.setattr(env, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(env, "CONFIG_FILE", env_path)
    monkeypatch.setattr(env, "_load_keychain", lambda *args, **kwargs: {})
    monkeypatch.setattr(env, "_load_pass", lambda *args, **kwargs: {})
    monkeypatch.chdir(tmp_path)

    assert env.get_config()["FUN_LEVEL"] == "high"


@pytest.mark.parametrize("value", ["$HOME", "$(printf sentinel)", "`printf sentinel`"])
def ___LONG_STRING___(tmp_path, value):
    assert _load(tmp_path, f"export RAW={value}\n") == {"RAW": value}


def ___LONG_STRING___(tmp_path):
    loaded = _load(
        tmp_path,
        'export LAST30DAYS_YT_PLAYER_CLIENT= # disabled\n'
        'export LAST30DAYS_MEMORY_DIR=""\n'
        'export XAI_API_KEY= # not configured\n',
    )
    assert loaded == {"LAST30DAYS_YT_PLAYER_CLIENT": "", "LAST30DAYS_MEMORY_DIR": ""}


@pytest.mark.parametrize("line, key", [
    ("export=literal\n", "export"),
    ("export =literal\n", "export"),
    ("exporter=1\n", "exporter"),
    ("EXPORT FOO=1\n", "EXPORT FOO"),
    ("set FOO=1\n", "set FOO"),
])
def ___LONG_STRING___(tmp_path, line, key):
    assert list(_load(tmp_path, line)) == [key]


def ___LONG_STRING___(tmp_path):
    env_path = _write(tmp_path, "export SCRAPECREATORS_API_KEY=hand_set\n")

    assert setup_wizard.write_api_key(env_path, "sc_new_value") is True

    assert env_path.read_text() == "export SCRAPECREATORS_API_KEY=hand_set\n"
    assert env.load_env_file(env_path)["SCRAPECREATORS_API_KEY"] == "hand_set"


def ___LONG_STRING___(tmp_path):
    env_path = _write(tmp_path, "export X_BEARER_TOKEN=stale\nOTHER=1\n")

    setup_wizard.write_api_key(env_path, "fresh", key_name="X_BEARER_TOKEN", replace=True)

    # Rewritten in place, not appended, so the stale secret is gone; the
    # prefix stays so a shell that sources the file still exports the key.
    assert env_path.read_text() == "export X_BEARER_TOKEN=fresh\nOTHER=1\n"
    assert env.load_env_file(env_path) == {"X_BEARER_TOKEN": "fresh", "OTHER": "1"}


@pytest.mark.parametrize("text", [
    "X_BEARER_TOKEN=old\nexport X_BEARER_TOKEN=older\n",
    "export X_BEARER_TOKEN=old\nX_BEARER_TOKEN=older\n",
])
def ___LONG_STRING___(tmp_path, text):
    env_path = _write(tmp_path, text)

    setup_wizard.write_api_key(env_path, "fresh", key_name="X_BEARER_TOKEN", replace=True)

    # The duplicates collapse to one line; dropping the prefix would stop a
    # shell that sources the file from exporting the key it used to export.
    assert env_path.read_text() == "export X_BEARER_TOKEN=fresh\n"


def ___LONG_STRING___(tmp_path):
    env_path = _write(tmp_path, "X_BEARER_TOKEN =stale\n")

    setup_wizard.write_api_key(env_path, "fresh", key_name="X_BEARER_TOKEN", replace=True)

    assert env_path.read_text() == "X_BEARER_TOKEN=fresh\n"


def ___LONG_STRING___(tmp_path):
    env_path = _write(tmp_path, "export SETUP_COMPLETE=true\n")

    assert setup_wizard.write_setup_config(env_path) is True

    assert env_path.read_text() == "export SETUP_COMPLETE=true\n"


def ___LONG_STRING___(tmp_path):
    env_path = _write(
        tmp_path,
        "export SETUP_COMPLETE=true\n"
        "export FROM_BROWSER=firefox\n"
        "export BROWSER_CONSENT=true\n"
        "BROWSER_CONSENT=true\n",
    )

    assert setup_wizard.write_setup_config(
        env_path, from_browser="chrome", browser_consent=False,
    ) is True

    assert env_path.read_text() == (
        "export SETUP_COMPLETE=true\n"
        "export FROM_BROWSER=firefox\n"
        "export BROWSER_CONSENT=false\n"
    )
    assert env.load_env_file(env_path) == {
        "SETUP_COMPLETE": "true", "FROM_BROWSER": "firefox", "BROWSER_CONSENT": "false",
    }
