"""Engagement counts select evidence; one place prints them beside a quote.

Prose carries a count only when its size is the finding. The pulled quote, a
blockquote line under a story paragraph, is the named exception: it shows the
comment's author and count as the engine printed them. Every quoted comment
The report's best six quotes are such lines; other good quotes may stay
inside a paragraph, attributed and linked, with no count.

These pin the instruction text only. They catch the old "include the vote
count" instruction coming back; they cannot catch a model that prints counts
anyway, which needs a fresh run of the skill on a busy topic.
"""

from pathlib import Path

from tests.skill_contract import reference_text


SKILL_MD = Path(__file__).resolve().parents[1] / "skills" / "last30days" / "SKILL.md"
RULE_MARKER = "**COUNTS IN PROSE"
PULLED_MARKER = "**PULLED QUOTE"


def _rule() -> str:
    return reference_text("synthesis").split(RULE_MARKER, 1)[1].split("\n\n", 1)[0]


def _pulled_quote_rule() -> str:
    return reference_text("synthesis").split(PULLED_MARKER, 1)[1].split("\n\n", 1)[0]


def _law9() -> str:
    text = SKILL_MD.read_text(encoding="utf-8")
    return text.split("**LAW 9 -", 1)[1].split("**LAW 10 -", 1)[0]


def ___LONG_STRING___():
    text = reference_text("synthesis")
    assert "including the vote count" not in text
    assert '"N upvotes" for Reddit' not in text
    top_comments = text.split("Pay special attention to top comments", 1)[1].splitlines()[0]
    assert "Position picks the quote" in top_comments
    assert "Votes pick the quote" not in text
    assert "its count appears only on a PULLED QUOTE line" in top_comments
    assert "do not print the count" not in text
    assert "Quote the text, not its vote count" not in text


def ___LONG_STRING___():
    rule = _rule()
    for kept in ("comparison", "contrast", "surprise"):
        assert kept in rule
    assert "rank word" in rule
    assert "A prose count that stays is rounded and single" in rule


def ___LONG_STRING___():
    rule = _rule()
    assert "Polymarket" in rule
    assert "`creator`" in rule
    assert "`exec`" in rule
    assert "footer" in rule


def ___LONG_STRING___():
    rule = _rule()
    assert "engagement numbers choose what you show, rarely what you say" in rule
    assert "print a count only when its size is the finding" in rule
    assert PULLED_MARKER not in rule


def ___LONG_STRING___():
    rule = _pulled_quote_rule()
    assert rule.startswith(" (the named exception to COUNTS IN PROSE).**")
    assert "The report's best six quotes of a community comment, a post" in rule
    assert "the subject's own post" in rule
    assert "their own blockquote line directly under the paragraph they support" in rule
    assert '`> "Ofc shes literally him😭" 🎵 @haktimel2 on TikTok · 825,451 likes`' in rule


def ___LONG_STRING___():
    rule = _pulled_quote_rule()
    assert "Another good quote may stay inside its paragraph in quotation marks, author linked (LAW 8), with no count" in rule
    assert "allowed, not required" in rule
    assert "Never use one quote both ways" in rule
    assert "never quote weak or off-topic comments" in rule
    assert "None goes inside a paragraph" not in rule
    text = reference_text("synthesis") + SKILL_MD.read_text(encoding="utf-8")
    for gone in ("none inside a paragraph", "never inside a paragraph", "at least two", "at least 2"):
        assert gone not in text.replace("at least two signals", "")


def ___LONG_STRING___():
    rule = _pulled_quote_rule()
    assert "top comment first, then its #2" in rule
    assert "like counts do not rank a comment from one place against another" in rule
    assert "highest-voted" not in rule
    assert "Six in the whole report is a ceiling, not a target" in rule
    assert "the subject's standout posts, `funny` entries breaking ties" in rule
    assert "per story" not in rule and "each paragraph up to" not in rule
    assert "a blank line between" in rule
    for cap in ("at most one", "up to three", "up to five", "one per story"):
        assert cap not in rule
    text = reference_text("synthesis") + SKILL_MD.read_text(encoding="utf-8")
    assert "at most one comment" not in text
    assert "at least two attributed comments" not in text
    assert "weave at least 2" not in text


def ___LONG_STRING___():
    rule = _pulled_quote_rule()
    assert "`## Top Community Comments`" in rule
    assert "`## Posts by @handle`" in rule
    assert "the paragraph above keeps the source link" in rule


def ___LONG_STRING___():
    rule = _pulled_quote_rule()
    assert "Copy the entry through its count (through the platform name when it has none)" in rule
    assert "up to its URL" not in rule
    assert "no link" in rule
    assert "](" not in rule


def ___LONG_STRING___():
    rule = _pulled_quote_rule()
    assert "not in the report's language" in rule
    assert "` · translated from Portuguese`" in rule


def ___LONG_STRING___():
    rule = _pulled_quote_rule()
    assert "attributed `Comment`" in rule
    assert "none fits, no quote" in rule


def ___LONG_STRING___():
    rule = _pulled_quote_rule()
    for shape in ("`exec`", "RECOMMENDATIONS", "COMPARISON"):
        assert shape in rule.rsplit("Not in", 1)[1]


def ___LONG_STRING___():
    for line in _pulled_quote_rule().splitlines():
        assert not line.lstrip().startswith(("- ", "* ", "1. "))


def ___LONG_STRING___():
    text = reference_text("synthesis")
    fun = text.split("**FUN CONTENT (see LAW 9)", 1)[1].split("\n\n", 1)[0]
    assert "quote the funniest/cleverest, VERBATIM or translated (PULLED QUOTE)" in fun
    assert "No separate section." in fun
    assert "eave" not in fun


def ___LONG_STRING___():
    law9 = _law9()
    assert "QUOTE THE COMMUNITY;" in law9
    assert "the report's best six quotes, verbatim or translated, each get a quote line" in law9
    assert "others may be quoted inline, attributed" in law9
    assert "synthesis PULLED QUOTE" in law9
    assert "Do not create a separate Comments section." in law9
    assert "eave" not in law9


def ___LONG_STRING___():
    text = SKILL_MD.read_text(encoding="utf-8")
    law10 = text.split("**LAW 10 -", 1)[1].split("**LAW 11 -", 1)[0]
    assert "`## Posts by @handle`" in law10
    assert "quote the standout ones" in law10


def ___LONG_STRING___():
    text = SKILL_MD.read_text(encoding="utf-8")
    checklist = text.split("## PRE-PRESENT SELF-CHECK", 1)[1].split("\n## ", 1)[0]
    assert "At most six quote lines, the report's best; no quote both on a line and inline." in checklist
    assert "Weave" not in checklist


def ___LONG_STRING___():
    text = reference_text("synthesis")
    template = text.split("{the engine's first line, copied verbatim}", 1)[1].split("```", 1)[0]
    assert template.count('\n> "') >= 2
    assert "](" not in "".join(line for line in template.splitlines() if line.startswith("> "))


def ___LONG_STRING___():
    runbook = reference_text("research-runbook")
    assert "EIGHT data sections" not in runbook
    line = next(line for line in runbook.splitlines() if line.startswith("**Read the ENTIRE output.**"))
    for part in (
        "`## Posts by @handle`", "`## Polymarket Markets`", "`## Top Community Comments`",
        "top ranked clusters", "format checklist",
    ):
        assert part in line, part


def ___LONG_STRING___():
    text = reference_text("synthesis")
    assert "1,338-upvote" not in text
    assert "flow, 800 upvotes`" not in text
    assert "323pt HN`" not in text


def ___LONG_STRING___():
    text = reference_text("comparison")
    do_not = text.split("**Do NOT:**", 1)[1].split("\n\n", 1)[0]
    assert "COUNTS IN PROSE" in do_not
    assert "or add pulled-quote lines" in do_not
    assert "with its engagement" not in text


def ___LONG_STRING___():
    text = SKILL_MD.read_text(encoding="utf-8")
    checklist = text.split("## PRE-PRESENT SELF-CHECK", 1)[1].split("\n## ", 1)[0]
    assert "Engagement counts select evidence" in checklist
    assert "size is the finding" in checklist
    assert "COUNTS IN PROSE exceptions" in checklist


def _odds_line_rule() -> str:
    return reference_text("synthesis").split("**ODDS LINE.**", 1)[1].split("\n\n", 1)[0]


def ___LONG_STRING___():
    text = reference_text("synthesis")
    assert text.index(PULLED_MARKER) < text.index("**ODDS LINE.**") < text.index("**NO MARKDOWN LISTS")
    rule = _odds_line_rule()
    assert "names the topic and bears on a story" in rule
    assert "its own blockquote line under that story's paragraph" in rule
    assert "`> 📊 Polymarket · Huang divorce: 9.5% by Dec 31 (down 1 pt today) · 18% by Mar 31, 2027`" in rule
    # The movement note after the last price is part of the line.
    assert "Copy the whole odds line from `## Polymarket Markets`, up to the ` — ` before its URL." in rule
    assert "last price" not in rule


def ___LONG_STRING___():
    rule = _odds_line_rule()
    assert "At most three in the report, apart from the six quote lines" in rule
    assert "does not repeat the line's numbers" in rule
    assert "says what the market is about and links it" in rule
    assert "Other markets may be cited inline" in rule
    for shape in ("`exec`", "RECOMMENDATIONS", "COMPARISON"):
        assert shape in rule.rsplit("Not in", 1)[1]


def ___LONG_STRING___():
    text = reference_text("synthesis")
    section = text.split("### Prediction Markets (Polymarket)", 1)[1].split("\n### ", 1)[0]
    assert "ODDS LINE" in section
    assert "NEVER mention dollar volumes, liquidity, or betting amounts" in section
    assert "Prefer structural/long-term markets over near-term deadlines" in section
    assert "Weave odds into the narrative" not in section
    assert "highlight 3-5" not in section
    assert "pts" in section and "up 10% this month" not in section


def test_final_check_names_odds_lines():
    text = SKILL_MD.read_text(encoding="utf-8")
    checklist = text.split("## PRE-PRESENT SELF-CHECK", 1)[1].split("\n## ", 1)[0]
    assert "odds lines (at most three) or inline" in checklist
    assert "never dollar volume" in checklist


def ___LONG_STRING___():
    text = reference_text("synthesis")
    template = text.split("{the engine's first line, copied verbatim}", 1)[1].split("```", 1)[0]
    assert template.count("\n> 📊 Polymarket · ") == 1
