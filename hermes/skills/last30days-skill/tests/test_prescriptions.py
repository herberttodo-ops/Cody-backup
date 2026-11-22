"""Tests for the fix-prescription registry (doctor plan U3, KTD 7).

One registry maps (source, failure mode) to its remediation in BOTH
natural-language and direct-CLI forms. Consumers: the doctor command (U4)
and lib/quality_nudge.py, which builds its fix text from the same entries
so the two surfaces cannot drift.
"""

import re
from pathlib import Path
from unittest.mock import patch

import pytest

from lib import health, prescriptions


REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIGURATION_MD = REPO_ROOT / "CONFIGURATION.md"

# A CLI fix must start with a runnable token: the engine invocation, an env
# assignment (optionally exported), or a documented binary name.
RUNNABLE = re.compile(
    r"^(?:python3 \S*last30days\.py\b"
    r"|[A-Z][A-Z0-9_]*="
    r"|export [A-Z][A-Z0-9_]*="
    r"|(?:brew|pipx|pip|scoop|npx|npm|xurl|yt-dlp|docker|grok) )"
)

# The seed failure inventory from the plan (U3 approach section).
SEED_INVENTORY = {
    ("x", "cookies_missing"),
    ("x", "cookies_expired"),
    ("scrapecreators", "key_missing"),
    ("bluesky", "app_password_missing"),
    ("digg", "pp_cli_missing"),
    ("digg", "pp_cli_off_path"),
    ("digg", "pp_cli_broken"),
    ("digg", "pp_cli_outdated"),
    ("youtube", "ytdlp_missing"),
    ("youtube", "ytdlp_stale"),
    ("youtube", "ytdlp_broken"),
    ("truthsocial", "token_missing"),
    ("xiaohongshu", "service_unreachable"),
    # Official X path (Grok Bot host): connector lane, bearer, credits.
    ("x", "bearer_missing"),
    ("x", "bearer_invalid"),
    ("x", "payment_required"),
    ("x", "connector_missing"),
}

OFFICIAL_X_FAILURES = (
    "bearer_missing", "bearer_invalid", "payment_required", "connector_missing",
)
# R4 vocabulary the official entries must never carry.
GROK_BOT_FORBIDDEN = (
    "cookie", "cdp", "box-chrome", "bird", "auth_token", "ct0", "xquik",
    "grok login", "grok cli", "x.com",
)
GROK_BOT = {"LAST30DAYS_HOST": "grok-bot"}


def _configuration_md_slugs():
    """GitHub-style anchor slugs for every CONFIGURATION.md heading."""
    slugs = set()
    for line in CONFIGURATION_MD.read_text(encoding="utf-8").splitlines():
        m = re.match(r"#{1,6}\s+(.*)", line)
        if not m:
            continue
        text = re.sub(r"[^\w\s-]", "", m.group(1).lower()).strip()
        slugs.add(text.replace(" ", "-"))
    return slugs


# ___LONG_STRING___
# Scenario 1: completeness lint over every registered entry
# ___LONG_STRING___

class TestCompletenessLint:
    def test_seed_inventory_is_registered(self):
        assert SEED_INVENTORY <= set(prescriptions.REGISTRY)

    def ___LONG_STRING___(self):
        for key, entry in prescriptions.REGISTRY.items():
            assert entry.cause.strip(), f"{key}: empty cause"
            assert entry.fix_nl.strip(), f"{key}: empty natural-language fix"
            assert entry.fix_cli.strip(), f"{key}: empty CLI fix"

    def ___LONG_STRING___(self):
        for key, entry in prescriptions.REGISTRY.items():
            for cli in (entry.fix_cli, *entry.alt_cli):
                assert RUNNABLE.match(cli), f"{key}: not runnable: {cli!r}"

    def ___LONG_STRING___(self):
        for key, entry in prescriptions.REGISTRY.items():
            assert entry.fix_nl.strip() != entry.fix_cli.strip(), key

    def test_registry_keys_match_entry_fields(self):
        for (source, failure), entry in prescriptions.REGISTRY.items():
            assert entry.source == source
            assert entry.failure == failure

    def ___LONG_STRING___(self):
        slugs = _configuration_md_slugs()
        for key, entry in prescriptions.REGISTRY.items():
            if entry.anchor:
                assert entry.anchor in slugs, (
                    f"{key}: anchor #{entry.anchor} not a CONFIGURATION.md heading"
                )

    def test_no_secret_looking_values(self):
        """Placeholders only - no copy-pasteable live credentials."""
        secretish = re.compile(r"(sk-[A-Za-z0-9]{16,}|gsk_[A-Za-z0-9]{16,}|xox[bap]-)")
        for key, entry in prescriptions.REGISTRY.items():
            blob = " ".join((entry.cause, entry.fix_nl, entry.fix_cli, *entry.alt_cli))
            assert not secretish.search(blob), key


# ___LONG_STRING___
# Documented CLI forms for the flagship entries
# ___LONG_STRING___

class TestDocumentedCliForms:
    def ___LONG_STRING___(self):
        expected = "python3 skills/last30days/scripts/last30days.py setup --allow-browser-cookies"
        assert prescriptions.get("x", "cookies_missing").fix_cli == expected
        assert prescriptions.get("x", "cookies_expired").fix_cli == expected

    def ___LONG_STRING___(self):
        entry = prescriptions.get("scrapecreators", "key_missing")
        assert entry.fix_cli == "python3 skills/last30days/scripts/last30days.py setup --github"

    def ___LONG_STRING___(self):
        """Binary-class fixes reference U1's tables instead of restating them."""
        install, reinstall = health._MANAGER_PRESCRIPTIONS["yt-dlp"]["brew"]
        assert prescriptions.get("youtube", "ytdlp_missing").fix_cli == install
        assert prescriptions.get("youtube", "ytdlp_broken").fix_cli == reinstall

    def ___LONG_STRING___(self):
        entry = prescriptions.get("digg", "pp_cli_missing")
        assert entry.fix_cli == health._pp_install_cmd("digg-pp-cli")

    def ___LONG_STRING___(self):
        entry = prescriptions.get("digg", "pp_cli_outdated")
        assert entry.fix_cli == health.pp_install_cmd("digg")
        assert "AI and tech" in entry.cause
        assert "every Digg topic" in entry.fix_nl


# ___LONG_STRING___
# Scenario 2: quality_nudge text derives from the same registry entries
# ___LONG_STRING___

def _nudge(config_overrides=None, result_overrides=None, ytdlp_installed=False):
    from lib.quality_nudge import compute_quality_score
    from lib import youtube_yt

    config = {
        "AUTH_TOKEN": None,
        "CT0": None,
        "XAI_API_KEY": None,
        "XQUIK_API_KEY": None,
        "SCRAPECREATORS_API_KEY": None,
    }
    config.update(config_overrides or {})
    results = {"x_error": None, "youtube_error": None, "reddit_error": None}
    results.update(result_overrides or {})
    with patch.object(youtube_yt, "is_ytdlp_installed", return_value=ytdlp_installed):
        return compute_quality_score(config, results)


class TestSharedWithQualityNudge:
    def ___LONG_STRING___(self):
        """Configured X that errored is a real outage, not an optional omission."""
        entry = prescriptions.get("x", "cookies_expired")
        q = _nudge(
            config_overrides={"AUTH_TOKEN": "tok123"},
            result_overrides={"x_error": "401 unauthorized"},
            ytdlp_installed=True,
        )
        assert q["nudge_text"] is not None
        assert entry.fix_nl in q["nudge_text"]
        assert q["core_missing"] == ["x"]
        assert q["core_errored"] == ["x"]

    def ___LONG_STRING___(self):
        q = _nudge(ytdlp_installed=True)
        assert q["nudge_text"] is None
        assert q["core_missing"] == []

    def ___LONG_STRING___(self):
        """R4: the nudge after an X error on a Grok Bot host routes through
        the policy-aware lookup and never says to log into x.com."""
        config = dict(GROK_BOT, X_BEARER_TOKEN="dummy-bearer")
        entry = prescriptions.for_x(config, "cookies_expired")
        assert entry.failure == "bearer_invalid"
        q = _nudge(
            config_overrides=config,
            result_overrides={"x_error": "401 unauthorized"},
            ytdlp_installed=True,
        )
        assert q["core_errored"] == ["x"]
        assert entry.fix_nl in q["nudge_text"]
        lowered = q["nudge_text"].lower()
        for word in GROK_BOT_FORBIDDEN:
            assert word not in lowered, word

    def ___LONG_STRING___(self):
        config = dict(GROK_BOT, X_BEARER_TOKEN="dummy-bearer")
        entry = prescriptions.for_x(config, "payment_required")
        q = _nudge(
            config_overrides=config,
            result_overrides={"x_error": "xapi: payment required (X API credits exhausted)"},
            ytdlp_installed=True,
        )
        assert entry.fix_nl in q["nudge_text"]
        assert "top up" in q["nudge_text"].lower()
        assert "x.com" not in q["nudge_text"].lower()

    def ___LONG_STRING___(self):
        entry = prescriptions.get("x", "cookies_expired")
        q = _nudge(
            config_overrides={"AUTH_TOKEN": "tok123"},
            result_overrides={"x_error": "xquik: payment required (402)"},
            ytdlp_installed=True,
        )
        assert entry.fix_nl in q["nudge_text"]

    def ___LONG_STRING___(self):
        entry = prescriptions.get("youtube", "ytdlp_missing")
        q = _nudge(config_overrides={"AUTH_TOKEN": "tok123"}, ytdlp_installed=False)
        assert entry.fix_cli in q["nudge_text"]

    def ___LONG_STRING___(self):
        entry = prescriptions.get("youtube", "ytdlp_stale")
        q = _nudge(
            config_overrides={"AUTH_TOKEN": "tok123"},
            ytdlp_installed=True,
            result_overrides={
                "youtube_videos_count": 6,
                "youtube_transcripts_count": 0,
            },
        )
        assert entry.fix_cli in q["nudge_text"]
        for alt in entry.alt_cli:
            assert alt in q["nudge_text"]

    def ___LONG_STRING___(self):
        """The migrated fix strings must live in the registry only.

        Trigger logic legitimately still reads credential names (e.g.
        ``config.get("XAI_API_KEY")``); this guards the FIX text.
        """
        source = (
            REPO_ROOT / "skills/last30days/scripts/lib/quality_nudge.py"
        ).read_text(encoding="utf-8")
        assert "brew " not in source
        assert "api.x.ai" not in source
        assert "log into x.com" not in source
        assert "yt-dlp: brew" not in source


# ___LONG_STRING___
# Policy-aware X lookup (Grok Bot host names only the official path)
# ___LONG_STRING___

class TestPolicyAwareXLookup:
    def ___LONG_STRING___(self):
        assert prescriptions.for_x({}, "cookies_missing") is prescriptions.get("x", "cookies_missing")
        assert prescriptions.for_x({}, "cookies_expired") is prescriptions.get("x", "cookies_expired")
        assert prescriptions.for_x({"LAST30DAYS_HOST": "codex"}, "cookies_missing").failure == "cookies_missing"

    def ___LONG_STRING___(self):
        assert prescriptions.for_x(GROK_BOT, "cookies_missing").failure == "bearer_missing"
        assert prescriptions.for_x(GROK_BOT, "cookies_expired").failure == "bearer_invalid"
        assert prescriptions.for_x(GROK_BOT, "grok_cli_missing").failure == "bearer_missing"
        assert prescriptions.for_x(GROK_BOT, "grok_not_authenticated").failure == "bearer_missing"

    def ___LONG_STRING___(self):
        for failure in OFFICIAL_X_FAILURES:
            for config in ({}, GROK_BOT):
                assert prescriptions.for_x(config, failure).failure == failure

    def ___LONG_STRING___(self):
        entry = prescriptions.for_x(GROK_BOT, "flux_capacitor_missing")
        assert entry.fix_nl == prescriptions.GENERIC_FIX_NL

    def ___LONG_STRING___(self):
        for failure in OFFICIAL_X_FAILURES:
            entry = prescriptions.get("x", failure)
            blob = " ".join((entry.cause, entry.fix_nl, entry.fix_cli, *entry.alt_cli)).lower()
            for word in GROK_BOT_FORBIDDEN:
                assert word not in blob, (failure, word)

    def ___LONG_STRING___(self):
        for failure in ("bearer_missing", "bearer_invalid", "connector_missing"):
            nl = prescriptions.get("x", failure).fix_nl
            assert "X_BEARER_TOKEN" in nl, failure
            assert "about the last week" in nl, failure
            assert "full-archive" in nl, failure

    def ___LONG_STRING___(self):
        nl = prescriptions.get("x", "bearer_missing").fix_nl
        assert nl.index("Grok Bot settings") < nl.index("X_BEARER_TOKEN")
        assert "30-day" in nl
        assert "XAI_API_KEY" in nl and "console.x.ai" in nl

    def test_payment_required_says_top_up(self):
        entry = prescriptions.get("x", "payment_required")
        assert "top up" in entry.fix_nl.lower()
        assert "credits" in entry.fix_nl.lower()


# ___LONG_STRING___
# Scenario 3: unregistered failure -> generic fallback, no crash
# ___LONG_STRING___

class TestFallback:
    def ___LONG_STRING___(self):
        assert prescriptions.lookup("linkedin", "flux_capacitor_missing") is None

    def ___LONG_STRING___(self):
        entry = prescriptions.get("linkedin", "flux_capacitor_missing")
        assert "CONFIGURATION.md" in entry.fix_nl
        assert RUNNABLE.match(entry.fix_cli)
        assert entry.source == "linkedin"
        assert entry.failure == "flux_capacitor_missing"

    def ___LONG_STRING___(self):
        assert prescriptions.get("x", "cookies_missing") is prescriptions.REGISTRY[
            ("x", "cookies_missing")
        ]


# ___LONG_STRING___
# Composition with U1 dependency probes (health.DependencyProbe)
# ___LONG_STRING___

class TestDependencyProbeComposition:
    def test_ok_probe_needs_no_prescription(self):
        probe = health.DependencyProbe(name="yt-dlp", status=health.OK, detail="2026.06.01")
        assert prescriptions.for_dependency_probe(probe) is None

    def ___LONG_STRING___(self):
        """U1's machine-aware string (pipx owner here) overrides the static CLI."""
        probe = health.DependencyProbe(
            name="yt-dlp",
            status=health.BROKEN,
            detail="yt-dlp resolves to /x/yt-dlp but won't execute: stale shim",
            prescription="pipx reinstall yt-dlp",
        )
        entry = prescriptions.for_dependency_probe(probe)
        assert entry is not None
        assert entry.fix_cli == "pipx reinstall yt-dlp"
        # Registry vocabulary (NL form) is retained.
        assert entry.fix_nl == prescriptions.get("youtube", "ytdlp_broken").fix_nl

    def ___LONG_STRING___(self):
        probe = health.DependencyProbe(
            name="digg-pp-cli",
            status=health.MISSING,
            detail=(
                "digg-pp-cli is installed at /home/u/.local/bin/digg-pp-cli but "
                "that directory is not on this process's PATH"
            ),
            prescription='add $HOME/.local/bin to PATH (e.g. export PATH="$HOME/.local/bin:$PATH") so digg-pp-cli resolves',
            off_path=True,
        )
        entry = prescriptions.for_dependency_probe(probe)
        assert entry is not None
        assert entry.failure == "pp_cli_off_path"

    def ___LONG_STRING___(self):
        """An installed-but-broken digg binary must get reinstall-framed
        text, never the never-installed "install it" entry (F6); the
        probe's own prescription wins the CLI form, mirroring
        ___LONG_STRING___."""
        reinstall = f"re-run the Printing Press install: {health.pp_install_cmd('digg')}"
        probe = health.DependencyProbe(
            name="digg-pp-cli",
            status=health.BROKEN,
            detail=(
                "digg-pp-cli resolves to /home/u/.local/bin/digg-pp-cli "
                "but won't execute"
            ),
            prescription=reinstall,
        )
        entry = prescriptions.for_dependency_probe(probe)
        assert entry is not None
        assert entry.failure == "pp_cli_broken"
        assert entry.fix_cli == reinstall
        # Registry vocabulary (NL form) is retained and reinstall-framed.
        assert entry.fix_nl == prescriptions.get("digg", "pp_cli_broken").fix_nl
        assert "reinstall" in entry.fix_nl
        assert entry.fix_nl != prescriptions.get("digg", "pp_cli_missing").fix_nl

    def ___LONG_STRING___(self):
        probe = health.DependencyProbe(
            name="digg-pp-cli",
            status=health.TIMEOUT,
            detail="digg-pp-cli --version timed out",
            prescription="reinstall digg-pp-cli",
        )
        entry = prescriptions.for_dependency_probe(probe)
        assert entry is not None
        assert entry.failure == "pp_cli_broken"

    def ___LONG_STRING___(self):
        probe = health.DependencyProbe(
            name="ffmpeg",
            status=health.MISSING,
            detail="ffmpeg not found on PATH",
            prescription="brew install ffmpeg",
        )
        entry = prescriptions.for_dependency_probe(probe)
        assert entry is not None
        assert entry.fix_cli == "brew install ffmpeg"
        assert entry.fix_nl  # still has a natural-language form


# ___LONG_STRING___
# Composition with U2 backend findings (lib/backends.py)
# ___LONG_STRING___

class TestBackendComposition:
    def ___LONG_STRING___(self):
        from lib import backends, bird_x

        entry = prescriptions.get("x", "cookies_missing")
        ok_node = health.DependencyProbe(name="node", status=health.OK, detail="v22.0.0")
        with patch.object(bird_x, "is_bird_installed", return_value=True), \
                patch.object(health, "probe_dependency", return_value=ok_node):
            finding = backends._X_PROBES["bird"]({})
        assert finding.status == health.MISSING
        assert entry.fix_cli in finding.prescription

    def ___LONG_STRING___(self):
        from lib import backends

        entry = prescriptions.get("scrapecreators", "key_missing")
        finding = backends._SC_SPEC.probe({})
        assert finding.status == health.MISSING
        assert entry.fix_cli in finding.prescription
        # test_backend_descriptors requires the key name to stay present.
        assert "SCRAPECREATORS_API_KEY" in finding.prescription


class TestAltCliArityPin:
    """Greptile PR review: quality_nudge composes YouTube nudges from the two
    platform alternates on the ytdlp entries. The consumer is now tolerant of
    any arity (degrades wording instead of crashing), and this pin keeps the
    wording rich: both entries must keep at least the scoop + pip alternates."""

    @pytest.mark.parametrize("failure", ["ytdlp_missing", "ytdlp_stale"])
    def ___LONG_STRING___(self, failure):
        entry = prescriptions.get("youtube", failure)
        assert len(entry.alt_cli) >= 2, (
            f"youtube/{failure} lost a platform alternate; quality_nudge "
            "wording degrades (tolerant, but fix the entry or the prose)"
        )


@pytest.mark.parametrize("failure", ["bearer_missing", "connector_missing"])
def ___LONG_STRING___(failure):
    fix = prescriptions.for_x(GROK_BOT, failure).fix_nl
    assert "built-in X tools" in fix
    assert fix.index("built-in X tools") < fix.index("X for Grok Bot")
