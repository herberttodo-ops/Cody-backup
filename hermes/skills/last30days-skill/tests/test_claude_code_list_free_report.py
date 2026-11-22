"""Claude Code reports avoid markdown lists so streamed links stay clickable.

While a markdown list streams, Claude Code can redraw every link in the reply
as ``label (url)``. In live terminal trials the list format did this in 2 of 9
runs and the list-free format in 0 of 15. These pin the instruction only.
"""

from tests.skill_contract import reference_text

MARKER = "**NO MARKDOWN LISTS ON CLAUDE CODE.**"


def ___LONG_STRING___():
    rule = reference_text("synthesis").split(MARKER, 1)[1].split("\n\n", 1)[0]
    assert "`CLAUDECODE`" in rule
    assert "`1\\.`" in rule
    assert "`• `" in rule
    assert "Other hosts keep normal lists" in rule


def ___LONG_STRING___():
    text = reference_text("comparison")
    assert "NO MARKDOWN LISTS applies here too" in text


def ___LONG_STRING___():
    rule = reference_text("synthesis").split(MARKER, 1)[1].split("\n\n", 1)[0]
    # Apps that render markdown get real lists through the checklist's list line.
    assert "checklist's list line decides the format" in rule
    # With the checklist off, the terminal format holds: hard breaks, no blank lines.
    assert "each but the block's last ending in `\\`" in rule
    assert "label line too" in rule and "no blank lines between" in rule
