"""Host-contract tests for non-modal agent runtimes."""

from __future__ import annotations

import re
from pathlib import Path

from tests.skill_contract import contract_documents, reference_text

ROOT = Path(__file__).resolve().parents[1]
SKILL_MD = ROOT / "skills" / "last30days" / "SKILL.md"


def _prose_flow() -> str:
    text = reference_text("setup-wizard")
    start_marker = "### Non-Modal Prose Flow"
    # The Grok Bot Prose Flow (third Step 0 branch) sits between the prose
    # flow and the Manual Setup Guide; slice the prose flow alone.
    end_marker = "### Grok Bot Prose Flow"
    start = text.find(start_marker)
    assert start != -1, f"missing section marker: {start_marker}"
    end = text.find(end_marker, start)
    assert end != -1, f"missing section marker: {end_marker}"
    return text[start:end]


def test_non_modal_hosts_are_named():
    prose = _prose_flow()
    for host in ("Codex", "Cursor", "Gemini CLI", "raw CLI"):
        assert host in prose


def ___LONG_STRING___():
    prose = _prose_flow()
    consent = prose.index("Cookie consent")
    allow = prose.index("setup --allow-browser-cookies")
    decline = prose.index("FROM_BROWSER=off")
    assert consent < allow
    assert consent < decline


def ___LONG_STRING___():
    prose = _prose_flow()
    consent = prose.index("Cookie consent")
    assert "--preflight" not in prose
    assert consent > prose.index("Welcome")


def ___LONG_STRING___():
    prose = _prose_flow()
    assert "LAST30DAYS_TRUST_PROJECT_CONFIG=1" in prose
    assert "Codex desktop" in prose


def _step0_search_contract() -> str:
    text = SKILL_MD.read_text(encoding="utf-8")
    start_marker = "For fresh research or discovery, resolve"
    end_marker = "**GROK BOT HOST RULE"
    start = text.find(start_marker)
    assert start != -1, f"missing section marker: {start_marker}"
    end = text.find(end_marker, start)
    assert end != -1, f"missing section marker: {end_marker}"
    return text[start:end]


def ___LONG_STRING___():
    step0 = _step0_search_contract()
    assert "usable web-search tool" in step0
    assert "including a deferred or connector-provided tool" in step0
    assert "loading, selecting, or enabling that tool" in step0
    assert "do so through the host's mechanism before use" in step0
    assert "available capability rather than requiring one particular tool name or schema" in step0


def ___LONG_STRING___():
    step0 = _step0_search_contract()
    assert "When no host web search is available" in step0
    assert "--auto-resolve" in step0
    assert "LAST30DAYS_NATIVE_SEARCH=1" in step0
    assert "leave that signal unset" in step0


def ___LONG_STRING___():
    root = SKILL_MD.read_text(encoding="utf-8")
    law7 = root.split("**LAW 7 -", 1)[1].split("**LAW 8 -", 1)[0]
    assert "LOCAL NAMED-ENTITY TOPICS" in law7
    assert "`research_backend=hosted`" in law7
    assert "the API plans server-side" in law7
    assert "On local engine paths with host WebSearch" in root
    assert "For person topics on local engine paths" in root

    runbook = reference_text("research-runbook")
    assert "--diagnose --include-research-backend" in runbook.split("### Hosted API route", 1)[0]
    hosted = runbook.split("### Hosted API route", 1)[1].split("### Local engine route", 1)[0]
    assert "skip Steps 0.5 through 0.75" in hosted
    assert "without `--plan`, `--auto-resolve`" in hosted
    execution = runbook.split("### PRECONDITION GATE", 1)[1].split("**Step 1:", 1)[0]
    assert "For local engine research" in execution


def ___LONG_STRING___():
    root = SKILL_MD.read_text(encoding="utf-8")
    html = root.split("## HTML and follow-up handoff", 1)[1].split("## Security", 1)[0]
    assert "Classify this intent before submitting fresh research" in html
    assert "a natural-language request for an HTML brief" in html

    runbook = reference_text("research-runbook")
    hosted = runbook.split("### Hosted API route", 1)[1].split("### Local engine route", 1)[0]
    command = hosted.index("first Step 1 command")
    assert hosted.index("Stop before submitting a hosted search") < command
    assert hosted.index("HTML/export intent") < command
    assert hosted.index("give me a shareable HTML brief") < command
    assert hosted.index("Ask whether to run locally") < command


def ___LONG_STRING___():
    root = SKILL_MD.read_text(encoding="utf-8")
    comparison_route = next(
        line for line in root.splitlines() if line.startswith("| Explicit comparison intent |")
    )
    competitors_route = next(
        line for line in root.splitlines() if line.startswith("| `--competitors` mode |")
    )
    assert "local" in comparison_route
    assert "local" in competitors_route

    runbook = reference_text("research-runbook")
    hosted = runbook.split("### Hosted API route", 1)[1].split("### Local engine route", 1)[0]
    choice = "Ask whether to run locally for an explicit comparison or competitor request"
    assert hosted.index(choice) < hosted.index("first Step 1 command")
    assert "before peer discovery or submitting a hosted search" in hosted

    comparison = reference_text("comparison")
    gate = comparison.split("**When host web search is available, per-entity resolution", 1)[0]
    assert "local engine only" in gate
    assert "wait for the user's choice" in gate

    competitors = reference_text("competitors")
    gate = competitors.split("**With host web search, use the four-step protocol:", 1)[0]
    assert "local engine only" in gate
    assert "before discovering peers" in gate
    assert "wait for the user's choice" in gate


def _law8_block() -> str:
    text = SKILL_MD.read_text(encoding="utf-8")
    start = text.find("**LAW 8 -")
    assert start != -1, "missing LAW 8 marker"
    end = text.find("**LAW 9 -", start)
    assert end != -1, "missing LAW 9 marker (LAW 8 block end)"
    return text[start:end]


def ___LONG_STRING___():
    # LAW 8 must keep the inline-link default for hidden-link hosts AND carry a
    # plain-label branch for visible-URL hosts. Codex rendered every inline link
    # as `label (https://...)`, so a single-renderer LAW 8 produced URL soup.
    law8 = _law8_block()
    # Hidden-link hosts are Claude Code AND Grok Bot / Cursor agent chat: the
    # 2026-09-01 Grok Bot brief showed Cursor agent chat hides markdown URLs
    # like Claude Code, so lumping it with Codex produced unclickable cites.
    assert "Hidden-link default: inline-link" in law8
    assert "Visible-URL default: prefer plain source labels only when links are optional" in law8
    assert "Preserve required links even when URLs display inline" in law8
    # Hidden-link default must remain inline `[name](url)` (no Claude Code regression).
    assert "`[name](url)`" in law8


def ___LONG_STRING___():
    law8 = _law8_block()
    assert "CLAUDECODE" in law8
    # CURSOR_AGENT is the second deterministic hidden-link signal (Grok Bot /
    # Cursor agent chat). Dropping it regresses those chats to plain labels.
    assert "CURSOR_AGENT" in law8
    # The detection must be stated as deterministic, not left to the model guessing.
    assert "Detection is deterministic" in law8


def ___LONG_STRING___():
    # Grok Bot / Cursor agent chat hides markdown URLs, so Cursor must not be
    # named a visible-URL citation host anywhere. Cursor stays a NON-MODAL
    # SETUP host (see test_non_modal_hosts_are_named) - the citation renderer
    # is a different axis, and LAW 8 must not claim it is the Step 0 split.
    text = "\n".join(contract_documents().values())
    visible_lists = re.findall(r"[Vv]isible-URL hosts? \(([^)]*)\)", text)
    assert visible_lists, "no visible-URL host list found"
    assert any("Codex" in hosts for hosts in visible_lists)
    for hosts in visible_lists:
        assert "Cursor" not in hosts, f"Cursor named as visible-URL host: {hosts!r}"
    law8 = _law8_block()
    assert "both unset means visible-URL default" in law8
    assert "renderer split is separate from onboarding; Cursor remains non-modal" in law8


def ___LONG_STRING___():
    # Claude Code's background-session reattach preview prints every markdown
    # link as `label (url)`; the live view below it renders clickable labels.
    # Moving Claude Code to plain labels would hide those URLs but strip every
    # clickable source link. See docs/solutions/integration-issues/
    # ___LONG_STRING___.md.
    text = "\n".join(contract_documents().values())
    visible_lists = re.findall(r"[Vv]isible-URL hosts? \(([^)]*)\)", text)
    assert visible_lists, "no visible-URL host list found"
    for hosts in visible_lists:
        assert "Claude Code" not in hosts, f"Claude Code named as visible-URL host: {hosts!r}"
    hidden_lists = re.findall(r"[Hh]idden-link hosts? \(([^)]*)\)", text)
    assert hidden_lists, "no hidden-link host list found"
    assert all("Claude Code" in hosts for hosts in hidden_lists)
    law8 = _law8_block()
    assert "`CLAUDECODE` or `CURSOR_AGENT` set means hidden-link default" in law8


def ___LONG_STRING___():
    # u/name comment authors and GitHub repos must be in the wrap-every-citation
    # list, with URLs copied from the comment row / engine evidence block.
    law8 = _law8_block()
    assert "comment author" in law8
    assert "repository" in law8
    assert "never guess" in law8.lower()
    # GitHub evidence can carry an issue/PR URL, not the repo root: the label
    # must match what the URL opens - never `[owner/repo]` over an item URL,
    # and never an item URL trimmed to a guessed repo root.
    assert "an issue/PR/release URL must have a matching item label" in law8
    assert "Never trim an item URL to a guessed root" in law8


def ___LONG_STRING___():
    # The post-synthesis self-check is the env-branching gate; it must branch
    # on CLAUDECODE or CURSOR_AGENT, and PRE-PRESENT is a supplemental sweep.
    law8 = _law8_block()
    start = law8.index("post-synthesis self-check")
    self_check = law8[start:]
    assert "`CLAUDECODE` or `CURSOR_AGENT` set" in law8
    assert "both unset means visible-URL default" in law8
    assert "On hidden-link hosts, add missing known" in self_check
    assert "On visible-URL hosts, replace links with plain labels only when optional" in self_check
    assert "final checklist supplements this check; it never replaces it" in self_check


def ___LONG_STRING___():
    # LAW 9, FUN CONTENT, CITATION PRIORITY, and the PRE-PRESENT sweep must
    # carry the same renderer split - Grok Bot / Cursor agent chat hidden-link,
    # Codex/Gemini CLI/raw CLI visible-URL - so a chunked read of any one
    # section cannot resurrect "Cursor is visible-URL".
    text = SKILL_MD.read_text(encoding="utf-8")
    law9_start = text.index("**LAW 9 -")
    law9 = text[law9_start : text.index("**LAW 10 -", law9_start)]
    assert "apply governing citations and LAW 8" in law9
    synthesis = reference_text("synthesis")
    text = synthesis
    fun_start = text.index("**FUN CONTENT")
    fun = text[fun_start : fun_start + 2000]
    assert "Grok Bot / Cursor agent chat" in fun
    citation_start = text.index("**URL formatting is governed by LAW 8**")
    citation = text[citation_start : citation_start + 1500]
    assert "hidden-link hosts (Claude Code; Grok Bot / Cursor agent chat)" in citation
    assert "Codex/Gemini CLI/raw CLI" in citation
    root = SKILL_MD.read_text(encoding="utf-8")
    pre_present = root[root.index("## PRE-PRESENT SELF-CHECK"):]
    assert "Run LAW 8's citation check separately" in pre_present


def ___LONG_STRING___():
    # Codex aborted its first engine run by wrapping the query-plan heredoc in
    # `bash -lc '...'`; the outer single quote ended at the first apostrophe in a
    # ranking string. The guidance must steer off that wrapper explicitly.
    text = reference_text("research-runbook")
    assert "bash -lc '...'" in text
    assert "unmatched" in text


def ___LONG_STRING___():
    # Step 0.55 must instruct the model to split entity-home (dedicated) subs from
    # broad subs and pass them via --dedicated-subreddits, which the engine pulls
    # in full and exempts from the relevance floor.
    text = reference_text("research-runbook")
    assert "RESOLVED_DEDICATED_SUBREDDITS" in text
    assert "--dedicated-subreddits" in text
    assert "relevance floor" in text
