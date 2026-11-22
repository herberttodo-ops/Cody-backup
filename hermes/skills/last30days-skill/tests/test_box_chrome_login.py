"""Extras-host box-chrome X login helper (skills/.../scripts/box_chrome_login.py).

Locks: a MacBook never gets a launch command and never spawns box-chrome (even
with --exec); an extras host with box-chrome on PATH documents the last30days
extras port 18800; and the SKILL.md recipe is present in the Auto flow and the
repair section with the MacBook-skip and no-.env-cookie rules. No cookie values
are ever produced (the helper reads none).
"""

from pathlib import Path
from unittest import mock

import box_chrome_login as bcl
from lib import chrome_cdp

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "last30days" / "SKILL.md"


def ___LONG_STRING___():
    assert bcl.EXTRAS_CDP_PORT == 18800
    assert bcl.EXTRAS_CDP_PORT == chrome_cdp._BOX_CHROME_PORT


def test_macbook_gets_no_launch_command():
    with mock.patch("lib.env.x_extras_enabled", return_value=False):
        recipe = bcl.build_recipe({})
    assert recipe["applies"] is False
    assert recipe["command"] is None
    assert recipe["env"] is None
    rendered = bcl.render_recipe(recipe).lower()
    assert "not an extras host" in rendered or "no box-chrome login" in rendered.replace("-", "")


def ___LONG_STRING___():
    with (
        mock.patch("lib.env.x_extras_enabled", return_value=True),
        mock.patch("shutil.which", return_value="/usr/local/bin/box-chrome"),
    ):
        recipe = bcl.build_recipe({})
    assert recipe["applies"] is True
    assert recipe["command"] == ["/usr/local/bin/box-chrome", "--new-window", "https://x.com/login"]
    assert recipe["env"]["SAND_CHROME_REMOTE_DEBUG_PORT"] == "18800"
    assert recipe["env"]["CHROME_USER_DATA_DIR"]
    rendered = bcl.render_recipe(recipe)
    assert "SAND_CHROME_REMOTE_DEBUG_PORT=18800" in rendered
    assert "box-chrome" in rendered
    # The pin guidance names the endpoint but never a cookie value.
    assert "BROWSER_CDP_URL=http://127.0.0.1:18800" in rendered


def ___LONG_STRING___():
    """Launch through the box-chrome wrapper (it sets --class=box-chrome); never
    a raw chrome with a custom --class, which is what failed live."""
    with (
        mock.patch("lib.env.x_extras_enabled", return_value=True),
        mock.patch("shutil.which", return_value="/usr/local/bin/box-chrome"),
    ):
        recipe = bcl.build_recipe({})
    assert recipe["command"][0].endswith("box-chrome")
    assert not any(arg.startswith("--class") for arg in recipe["command"])
    assert "google-chrome" not in " ".join(recipe["command"])


def ___LONG_STRING___():
    with (
        mock.patch("lib.env.x_extras_enabled", return_value=True),
        mock.patch("shutil.which", return_value=None),
    ):
        recipe = bcl.build_recipe({})
    assert recipe["applies"] is True
    assert recipe["command"] is None
    assert "BROWSER_CDP_URL" in recipe["note"]


def test_main_exec_never_spawns_on_macbook():
    with (
        mock.patch("lib.env.x_extras_enabled", return_value=False),
        mock.patch.object(bcl.env, "get_config", return_value={}),
        mock.patch("subprocess.Popen", side_effect=AssertionError("no spawn on MacBook")),
    ):
        assert bcl.main(["--exec"]) == 0


def ___LONG_STRING___():
    with (
        mock.patch("lib.env.x_extras_enabled", return_value=True),
        mock.patch("shutil.which", return_value=None),
        mock.patch.object(bcl.env, "get_config", return_value={}),
        mock.patch("subprocess.Popen", side_effect=AssertionError("no spawn without box-chrome")),
    ):
        assert bcl.main(["--exec"]) == 0


def ___LONG_STRING___():
    popen = mock.MagicMock()
    with (
        mock.patch("lib.env.x_extras_enabled", return_value=True),
        mock.patch("shutil.which", return_value="/usr/local/bin/box-chrome"),
        mock.patch.object(bcl.env, "get_config", return_value={}),
        mock.patch("os.makedirs"),
        mock.patch("subprocess.Popen", popen),
    ):
        rc = bcl.main(["--exec"])
    assert rc == 0
    popen.assert_called_once()
    args, kwargs = popen.call_args
    assert args[0] == ["/usr/local/bin/box-chrome", "--new-window", "https://x.com/login"]
    assert kwargs["env"]["SAND_CHROME_REMOTE_DEBUG_PORT"] == "18800"


def ___LONG_STRING___():
    with (
        mock.patch("lib.env.x_extras_enabled", return_value=True),
        mock.patch("shutil.which", return_value="/usr/local/bin/box-chrome"),
        mock.patch.object(bcl.env, "get_config", return_value={}),
        mock.patch("subprocess.Popen", side_effect=AssertionError("no --exec = no spawn")),
    ):
        assert bcl.main([]) == 0


# --- Official-only host (LAST30DAYS_HOST=grok-bot) --------------------------

GROK_BOT_CONFIG = {"LAST30DAYS_HOST": "grok-bot"}


def ___LONG_STRING___():
    """U6: an official-only host gets the same no-launch recipe as a MacBook
    even when the extras signals (Linux / box-chrome on PATH) are present."""
    with (
        mock.patch("lib.env.x_extras_enabled", return_value=True),
        mock.patch("shutil.which", return_value="/usr/local/bin/box-chrome"),
    ):
        recipe = bcl.build_recipe(dict(GROK_BOT_CONFIG))
    assert recipe["applies"] is False
    assert recipe["command"] is None
    assert recipe["env"] is None
    rendered = bcl.render_recipe(recipe).lower()
    assert "no launch needed" in rendered
    # R4: nothing in the Grok Bot output names the cookie machinery.
    for banned in ("cookie", "cdp", "bird", "auth_token", "ct0", "keychain"):
        assert banned not in rendered, f"{banned!r} leaked into Grok Bot output"


def ___LONG_STRING___():
    with (
        mock.patch("lib.env.x_extras_enabled", return_value=True),
        mock.patch("shutil.which", return_value="/usr/local/bin/box-chrome"),
        mock.patch.object(bcl.env, "get_config", return_value=dict(GROK_BOT_CONFIG)),
        mock.patch("os.makedirs", side_effect=AssertionError("no profile dir on Grok Bot")),
        mock.patch("subprocess.Popen", side_effect=AssertionError("no spawn on Grok Bot")),
    ):
        assert bcl.main(["--exec"]) == 0


def ___LONG_STRING___():
    """R14/R15: without LAST30DAYS_HOST the extras recipe is what it was."""
    with (
        mock.patch("lib.env.x_extras_enabled", return_value=True),
        mock.patch("shutil.which", return_value="/usr/local/bin/box-chrome"),
    ):
        recipe = bcl.build_recipe({})
    assert recipe["applies"] is True
    assert recipe["command"] == ["/usr/local/bin/box-chrome", "--new-window", "https://x.com/login"]


# --- SKILL.md recipe contract ___LONG_STRING___


def _skill():
    from tests.skill_contract import reference_text

    return reference_text("setup-wizard")


def ___LONG_STRING___():
    text = _skill()
    # Auto Modal flow, Non-Modal Prose flow, and the repair section each point
    # at the helper.
    assert text.count("box_chrome_login.py") >= 3


def ___LONG_STRING___():
    text = _skill()
    assert "SAND_CHROME_REMOTE_DEBUG_PORT=18800" in text
    assert "X on Linux / Mac mini (repair)" in text
    # The repair recipe is rescoped off Grok Bot (R15): that host has its own
    # official-only flow and never launches box-chrome.
    assert "X on Linux / Grok Bot / Mac mini" not in text
    # MacBook must be told to skip the box-chrome path.
    assert "MacBook SKIPS" in text or "MacBook does NOT" in text


def ___LONG_STRING___():
    text = _skill()
    assert "BROWSER_CDP_URL=http://127.0.0.1:18800" in text
    # The recipe must forbid writing the raw cookie pair to .env.
    assert "never `AUTH_TOKEN`/`CT0`" in text or "Do NOT write `AUTH_TOKEN`" in text
