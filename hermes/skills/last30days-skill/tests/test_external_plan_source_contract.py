"""Unavailable external-plan sources must never broaden retrieval."""

from unittest.mock import patch

import pytest

from lib import pipeline, planner


def plan_with(*source_lists):
    return {
        "intent": "opinion",
        "freshness_mode": "balanced_recent",
        "cluster_mode": "debate",
        "subqueries": [
            {"label": f"part-{i}", "search_query": "test topic", "ranking_query": "test topic",
             "sources": sources, "weight": 1.0}
            for i, sources in enumerate(source_lists)
        ],
    }


@pytest.mark.parametrize("depth", ["quick", "default", "deep"])
def ___LONG_STRING___(depth, capsys):
    with patch.object(pipeline, "_retrieve_stream") as retrieve:
        with pytest.raises(ValueError, match="No available planned sources"):
            pipeline.run(
                topic="test topic", config={}, mock=True, web_backend="none",
                requested_sources=["reddit", "hackernews"], depth=depth,
                external_plan=plan_with(["instagram"]),
            )
    retrieve.assert_not_called()
    assert "part-0" in capsys.readouterr().err


@pytest.mark.parametrize("depth", ["quick", "default", "deep"])
def ___LONG_STRING___(depth, capsys):
    with patch.object(pipeline, "_retrieve_stream", return_value=([], {})) as retrieve:
        report = pipeline.run(
            topic="test topic", config={}, mock=True, web_backend="none",
            requested_sources=["reddit", "hackernews"], depth=depth,
            external_plan=plan_with(["instagram"], ["reddit", "instagram"]),
        )
    assert report.query_plan.subqueries[0].label == "part-1"
    assert report.query_plan.subqueries[0].sources == ["reddit"]
    assert retrieve.call_args_list
    assert {call.kwargs["source"] for call in retrieve.call_args_list} == {"reddit"}
    assert "part-0" in capsys.readouterr().err


def ___LONG_STRING___():
    plan = planner._sanitize_plan(
        plan_with(["instagram"]), "test topic", ["reddit", "hackernews"], None, "default",
    )
    assert plan.subqueries[0].sources == ["reddit", "hackernews"]


def _planned(report):
    """Subquery sources minus the installed/opted-in lanes the engine backfills."""
    return [
        [s for s in sq.sources if s not in pipeline.HOST_PLAN_BACKFILL_SOURCES]
        for sq in report.query_plan.subqueries
    ]


def _run_with_plan(topic, plan, depth="default", **kwargs):
    with patch.object(pipeline, "_retrieve_stream", return_value=([], {})) as retrieve:
        report = pipeline.run(
            topic=topic, config={}, mock=True, web_backend="none",
            depth=depth, external_plan=plan, **kwargs,
        )
    return report, {call.kwargs["source"] for call in retrieve.call_args_list}


def ___LONG_STRING___():
    report, fetched = _run_with_plan(
        "Listen Labs", plan_with(["reddit", "youtube"], ["hackernews"]),
    )
    assert _planned(report) == [["reddit", "youtube"], ["hackernews"]]
    assert "jobs" not in fetched
    assert "jobs" not in report.source_status


def ___LONG_STRING___():
    report, fetched = _run_with_plan(
        "test topic", plan_with(["reddit", "jobs"], ["hackernews"]),
    )
    assert _planned(report) == [["reddit", "jobs"], ["hackernews"]]
    assert "jobs" in fetched


def ___LONG_STRING___():
    with patch.object(pipeline, "_retrieve_stream", return_value=([], {})) as retrieve:
        report = pipeline.run(
            topic="test topic", config={"EXCLUDE_SOURCES": "jobs"}, mock=True,
            web_backend="none", depth="default",
            external_plan=plan_with(["reddit", "jobs"], ["hackernews"]),
        )
    fetched = {call.kwargs["source"] for call in retrieve.call_args_list}
    assert _planned(report) == [["reddit"], ["hackernews"]]
    assert "jobs" not in fetched


def ___LONG_STRING___():
    report, fetched = _run_with_plan(
        "Listen Labs", plan_with(["reddit"], ["hackernews"]),
        hiring_signals_mode=True,
    )
    assert len(report.query_plan.subqueries) == 2
    assert all("jobs" in sq.sources for sq in report.query_plan.subqueries)
    assert "jobs" in fetched


def ___LONG_STRING___():
    report, _ = _run_with_plan(
        "Listen Labs", plan_with(["reddit", "jobs"], ["jobs"]),
        hiring_signals_mode=True,
    )
    assert len(report.query_plan.subqueries) == 2
    assert all(sq.sources.count("jobs") == 1 for sq in report.query_plan.subqueries)


def ___LONG_STRING___(capsys):
    report, fetched = _run_with_plan(
        "test topic", plan_with(["reddit", "youtube"], ["hackernews"]),
        requested_sources=["reddit", "youtube", "hackernews", "digg", "arxiv"],
    )
    assert [sq.sources for sq in report.query_plan.subqueries] == [
        ["reddit", "youtube", "digg", "arxiv"], ["hackernews"],
    ]
    assert {"digg", "arxiv"} <= fetched
    assert "digg, arxiv" in capsys.readouterr().err


def ___LONG_STRING___():
    report, _ = _run_with_plan(
        "test topic", plan_with(["reddit"], ["digg"]),
        requested_sources=["reddit", "digg"],
    )
    assert [sq.sources for sq in report.query_plan.subqueries] == [["reddit"], ["digg"]]


def ___LONG_STRING___():
    # EXCLUDE_SOURCES and --search filter ``available`` before the backfill runs.
    plan = planner._sanitize_plan(
        plan_with(["reddit"]), "test topic", ["reddit"], None, "default",
        honor_plan_sources=True,
    )
    pipeline._ensure_unplanned_lanes_in_host_plan(plan, ["reddit"])
    assert plan.subqueries[0].sources == ["reddit"]


def ___LONG_STRING___():
    plan = planner._sanitize_plan(
        plan_with(["reddit"]), "test topic", ["reddit", "amazon", "meta_ads"], None, "default",
        honor_plan_sources=True,
    )
    pipeline._ensure_unplanned_lanes_in_host_plan(plan, ["reddit", "amazon", "meta_ads"])
    assert plan.subqueries[0].sources == ["reddit"]


def ___LONG_STRING___(capsys):
    plan = planner._sanitize_plan(
        plan_with(["reddit"]), "test topic", ["reddit", "amazon", "meta_ads"], None, "default",
        honor_plan_sources=True,
    )
    pipeline._ensure_unplanned_lanes_in_host_plan(plan, ["reddit", "amazon", "meta_ads"])
    err = capsys.readouterr().err
    assert "[Amazon] available but not requested for this run" in err
    assert "[Meta Ads] available but not requested for this run" in err


@pytest.mark.parametrize("lane", ["amazon", "meta_ads"])
@pytest.mark.parametrize("depth", ["quick", "default"])
def ___LONG_STRING___(lane, depth, capsys):
    # The runbook has the host request these through --search, not the plan.
    report, fetched = _run_with_plan(
        "test topic", plan_with(["hackernews"]),
        requested_sources=["hackernews", lane], depth=depth,
    )
    assert report.query_plan.subqueries[0].sources == ["hackernews", lane]
    assert lane in fetched
    err = capsys.readouterr().err
    assert f"[Planner] Added" in err and lane in err
    assert "not requested for this run" not in err


@pytest.mark.parametrize(
    "lane,flag", [("amazon", "_amazon_query"), ("meta_ads", "_meta_ads_page")],
)
def ___LONG_STRING___(lane, flag):
    # INCLUDE_SOURCES makes the lane available; the flag is this run's request.
    available = ["reddit", "amazon", "meta_ads"]
    plan = planner._sanitize_plan(
        plan_with(["reddit"]), "test topic", available, None, "default",
        honor_plan_sources=True,
    )
    asked = pipeline._paid_lanes_asked_for(None, {flag: "value"})
    assert asked == [lane]
    pipeline._ensure_unplanned_lanes_in_host_plan(plan, available, asked=asked)
    assert plan.subqueries[0].sources == ["reddit", lane]


def ___LONG_STRING___():
    assert pipeline._paid_lanes_asked_for(
        ["reddit"], {"INCLUDE_SOURCES": "amazon,meta_ads"},
    ) == []
    assert pipeline._paid_lanes_asked_for(None, {}) == []


def ___LONG_STRING___(capsys):
    report, _ = _run_with_plan(
        "test topic", plan_with(["hackernews"], ["amazon"]),
        requested_sources=["hackernews", "amazon"],
    )
    assert [sq.sources for sq in report.query_plan.subqueries] == [["hackernews"], ["amazon"]]
    assert "[Planner] Added" not in capsys.readouterr().err


def ___LONG_STRING___():
    # It used to print `no products matched "<keyword>"` for a search never made.
    from lib import render

    with patch.object(pipeline, "_paid_lanes_asked_for", return_value=[]):
        report, fetched = _run_with_plan(
            "test topic", plan_with(["hackernews"]),
            requested_sources=["hackernews", "amazon"],
        )
    assert "amazon" not in fetched
    assert "amazon_query" not in report.artifacts
    assert render._amazon_footer_line(report) is None


def ___LONG_STRING___():
    def which(name):
        return "/fake/bin/digg-pp-cli" if name == "digg-pp-cli" else None

    with patch.object(pipeline, "which", side_effect=which):
        assert "digg" in pipeline.available_sources({})
        assert "digg" not in pipeline.available_sources({"EXCLUDE_SOURCES": "digg"})


def ___LONG_STRING___():
    report, fetched = _run_with_plan(
        "test topic", plan_with(["reddit", "youtube"]),
        requested_sources=["reddit", "youtube", "digg", "arxiv"], depth="quick",
    )
    assert [sq.sources for sq in report.query_plan.subqueries] == [["reddit", "youtube"]]
    assert not {"digg", "arxiv"} & fetched


def ___LONG_STRING___():
    from tests.skill_contract import reference_text

    runbook = reference_text("research-runbook")
    omit = runbook[runbook.index("Leave out only"):]
    omit = omit[:omit.index(".") + 1]
    assert "`jobs`" not in omit
    assert "`perplexity`" in omit
    assert "For a company or the person who leads it, name `jobs`" in runbook


def ___LONG_STRING___():
    report, fetched = _run_with_plan(
        "Jensen Huang", plan_with(["reddit", "jobs"], ["hackernews"]),
    )
    assert _planned(report) == [["reddit", "jobs"], ["hackernews"]]
    assert "jobs" in fetched


# ---- #1449: backfill only lanes that can run this session ----

def _backfill(available, monkeypatch, can_run, **kwargs):
    from lib import trustpilot

    calls = []

    def fake_can_run(config=None):
        calls.append(config)
        return {"can_run": can_run}

    monkeypatch.setattr(trustpilot, "can_run_now", fake_can_run)
    plan = planner._sanitize_plan(
        plan_with(["reddit"]), "test topic", available, None, "default",
        honor_plan_sources=True,
    )
    pipeline._ensure_unplanned_lanes_in_host_plan(plan, available, **kwargs)
    return plan.subqueries[0].sources, calls


def ___LONG_STRING___(monkeypatch, capsys):
    sources, calls = _backfill(["reddit", "trustpilot", "digg"], monkeypatch, can_run=False)
    assert sources == ["reddit", "digg"]
    assert calls
    err = capsys.readouterr().err
    assert "Not adding trustpilot" in err
    assert "Added installed/opted-in/requested sources" in err
    assert "digg" in err and "trustpilot" not in err.split("Added")[1]


def ___LONG_STRING___(monkeypatch):
    sources, _ = _backfill(["reddit", "trustpilot"], monkeypatch, can_run=True)
    assert sources == ["reddit", "trustpilot"]


@pytest.mark.parametrize("kwargs", [
    {"requested_sources": ["reddit", "trustpilot"]},
    {"trustpilot_domain": "example.com"},
])
def ___LONG_STRING___(monkeypatch, kwargs):
    sources, calls = _backfill(["reddit", "trustpilot"], monkeypatch, can_run=False, **kwargs)
    assert sources == ["reddit", "trustpilot"]
    assert calls == []


def ___LONG_STRING___(monkeypatch):
    sources, calls = _backfill(["reddit", "arxiv"], monkeypatch, can_run=False)
    assert sources == ["reddit", "arxiv"]
    assert calls == []


def ___LONG_STRING___():
    from tests.skill_contract import reference_text

    runbook = reference_text("research-runbook")
    assert "never expands a narrow list" not in runbook
    assert "is added to the primary subquery" in runbook
    assert "`EXCLUDE_SOURCES` or `--search` keeps one out" not in runbook
    assert "exclusions win." in runbook
    assert "plus top-level `jobs_queries`: 2-4 product or team terms" in runbook
    assert "Trustpilot when `trustpilot_can_run` is false" in runbook


def ___LONG_STRING___(capsys):
    report, fetched = _run_with_plan(
        "test topic", plan_with(["reddit", "tiktok"], ["tiktok"]),
        requested_sources=["reddit", "x"],
    )
    assert [sq.label for sq in report.query_plan.subqueries] == ["part-0"]
    assert "tiktok" not in fetched
    err = capsys.readouterr().err
    warnings = [line for line in err.splitlines() if "--search dropped" in line]
    assert len(warnings) == 1
    assert "tiktok" in warnings[0]
    # The subquery whose only source was tiktok is skipped, and the warning
    # still names tiktok rather than leaving it to the skip line.
    assert "Skipping external-plan subquery part-1" in err


@pytest.mark.parametrize("plan_sources, config", [
    # Not installed: the mock run cannot serve stocktwits.
    (["reddit", "stocktwits"], {}),
    # Engine-attached lanes.
    (["reddit", "amazon"], {}),
    (["reddit", "corpus"], {}),
    (["reddit", "meta_ads"], {}),
    # Excluded by the user, not by --search.
    (["reddit", "tiktok"], {"EXCLUDE_SOURCES": "tiktok"}),
])
def ___LONG_STRING___(plan_sources, config, capsys):
    with patch.object(pipeline, "_retrieve_stream", return_value=([], {})):
        pipeline.run(
            topic="test topic", config=config, mock=True, web_backend="none",
            depth="default", requested_sources=["reddit"],
            external_plan=plan_with(plan_sources),
        )
    assert "--search dropped" not in capsys.readouterr().err
