"""Regression tests for entity grounding on generic, entity-less topics."""

import pytest

from lib import rerank

GENERIC_TOPIC = "AI code review bottleneck: can reviewers still judge AI-produced work"


def ___LONG_STRING___():
    entity = rerank._primary_entity(GENERIC_TOPIC)
    assert "code review" in entity.lower(), (
        f"expected the subject phrase to survive intent-modifier stripping, got {entity!r}"
    )


def ___LONG_STRING___():
    entity = rerank._primary_entity(GENERIC_TOPIC)
    off_topic = (
        "INSTEAD OF WATCHING NETFLIX TONIGHT Spend 1 hour with this Claude AI FULL "
        "COURSE that teaches you how to BUILD and AUTOMATE anything"
    )
    assert not rerank._entity_grounded(off_topic, entity), (
        "a course advertisement sharing only the token 'AI' should not count as grounded"
    )


def ___LONG_STRING___():
    entity = rerank._primary_entity(GENERIC_TOPIC)
    unrelated = "my weekend project: a barcode scanner written in rust"
    assert not rerank._entity_grounded(unrelated, entity), (
        "'code' inside 'barcode' should not ground an unrelated candidate"
    )


@pytest.mark.parametrize(
    "unrelated",
    [
        "This code works",
        "The review was helpful",
        "Work is changing",
    ],
)
def ___LONG_STRING___(unrelated):
    entity = rerank._primary_entity(GENERIC_TOPIC)
    assert not rerank._entity_grounded(unrelated, entity)


def ___LONG_STRING___():
    entity = rerank._primary_entity(GENERIC_TOPIC)
    on_topic = "our reviewers cannot keep up with generated diffs"
    assert rerank._entity_grounded(on_topic, entity)


def test_on_topic_item_is_grounded_control():
    entity = rerank._primary_entity(GENERIC_TOPIC)
    on_topic = "How to keep QA from being a giant bottleneck with AI coding"
    assert rerank._entity_grounded(on_topic, entity)


def ___LONG_STRING___():
    assert rerank._entity_grounded("Golang concurrency patterns", "Go programming")
