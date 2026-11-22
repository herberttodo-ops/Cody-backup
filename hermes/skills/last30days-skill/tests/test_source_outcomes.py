import socket
import urllib.error
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

import pytest

from lib import (
    bird_x,
    health,
    http,
    jobs,
    pipeline,
    reddit,
    reddit_listing,
    render,
    schema,
    youtube_yt,
)


def _report(*, source_status=None, items_by_source=None, errors_by_source=None):
    return schema.Report(
        topic="test topic",
        range_from="2026-06-10",
        range_to="2026-07-10",
        generated_at="2026-07-10T18:22:03Z",
        provider_runtime=schema.ProviderRuntime(
            reasoning_provider="gemini",
            planner_model="test-planner",
            rerank_model="test-reranker",
        ),
        query_plan=schema.QueryPlan(
            intent="general",
            freshness_mode="balanced_recent",
            cluster_mode="story",
            raw_topic="test topic",
            subqueries=[
                schema.SubQuery(
                    label="primary",
                    search_query="test topic",
                    ranking_query="test topic",
                    sources=["x"],
                )
            ],
            source_weights={"x": 1.0},
        ),
        clusters=[],
        ranked_candidates=[],
        items_by_source=items_by_source or {},
        errors_by_source=errors_by_source or {},
        source_status=source_status or {},
    )


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (http.HTTPError("HTTP 429", status_code=429), schema.RATE_LIMITED),
        (http.HTTPError("HTTP 401", status_code=401), schema.AUTH_FAILED),
        (http.HTTPError("HTTP 402", status_code=402), schema.PAYMENT_REQUIRED),
        (http.HTTPError("HTTP 403", status_code=403), schema.AUTH_FAILED),
        (http.HTTPError("Invalid JSON response"), schema.SCHEMA_DRIFT),
        (http.HTTPError("Connection error: reset"), schema.UNREACHABLE),
        (http.HTTPError("Request timed out"), health.TIMEOUT),
    ],
)
def ___LONG_STRING___(error, expected):
    assert error.outcome_state == expected


@patch("lib.http.time.sleep")
@patch("lib.http.urllib.request.urlopen")
def ___LONG_STRING___(mock_urlopen, _mock_sleep):
    mock_urlopen.side_effect = urllib.error.URLError(
        socket.gaierror(-2, "Name or service not known")
    )

    with pytest.raises(http.HTTPError) as caught:
        http.get("https://unreachable.example", retries=1)

    assert caught.value.outcome_state == schema.UNREACHABLE


def ___LONG_STRING___():
    assert bird_x.classify_run_failure("likely Twitter anti-bot interstitial") == schema.SCHEMA_DRIFT
    assert reddit.classify_run_failure("blocked by Reddit interstitial") == schema.RATE_LIMITED
    assert youtube_yt.classify_run_failure("Sign in to confirm you're not a bot") == schema.RATE_LIMITED
    assert youtube_yt.classify_run_failure("Search timed out after 1s") == health.TIMEOUT


def ___LONG_STRING___():
    clean = schema.RetrievalBundle()
    clean.mark_attempted("x")

    failed = schema.RetrievalBundle()
    failed.mark_attempted("x")
    failed.record_failure("x", schema.RATE_LIMITED, "HTTP 429")

    assert clean.source_status["x"].state == schema.NO_RESULTS
    assert failed.source_status["x"].state == schema.RATE_LIMITED
    assert failed.source_status["x"].fix_hint == "doctor"


@patch("lib.http.urllib.request.urlopen")
def ___LONG_STRING___(mock_urlopen):
    mock_urlopen.side_effect = urllib.error.HTTPError(
        "https://api.example.com",
        401,
        "Unauthorized",
        {},
        None,
    )

    def source_that_launders_failure(*_args, **_kwargs):
        try:
            http.get("https://api.example.com", retries=1)
        except http.HTTPError:
            return [], {}
        raise AssertionError("request should have failed")

    with patch("lib.pipeline._retrieve_stream_impl", side_effect=source_that_launders_failure):
        items, artifact = pipeline._retrieve_stream()

    assert items == []
    assert artifact["_source_outcome"]["state"] == schema.AUTH_FAILED


@patch("lib.http.time.sleep")
@patch("lib.http.urllib.request.urlopen")
def ___LONG_STRING___(mock_urlopen, _mock_sleep):
    mock_urlopen.side_effect = urllib.error.HTTPError(
        "https://api.scrapecreators.com/v1/reddit/search",
        429,
        "Too Many Requests",
        {},
        None,
    )

    with http.capture_failures() as failures:
        result = reddit.search_reddit(
            "test topic",
            "2026-06-10",
            "2026-07-10",
            depth="quick",
            token="dummy-token",
        )

    assert result["items"] == []
    assert failures[-1].outcome_state == schema.RATE_LIMITED


def _reddit_429(url="https://www.reddit.com/svc/shreddit/search/"):
    return urllib.error.HTTPError(url, 429, "Too Many Requests", {}, None)


@patch("lib.http.time.sleep")
@patch("lib.http.urllib.request.urlopen")
def ___LONG_STRING___(mock_urlopen, _mock_sleep):
    mock_urlopen.side_effect = _reddit_429(
        "https://www.reddit.com/svc/shreddit/community-more-posts/hot/"
    )

    with http.capture_failures() as failures:
        posts = reddit_listing.fetch_listings(["example"], depth="quick", query="test topic")

    assert posts == []
    assert failures[-1].outcome_state == schema.RATE_LIMITED


@patch("lib.http.time.sleep")
@patch("lib.http.urllib.request.urlopen")
def ___LONG_STRING___(mock_urlopen, _mock_sleep):
    mock_urlopen.side_effect = _reddit_429(
        "https://www.reddit.com/svc/shreddit/community-more-posts/rising/"
    )

    with http.capture_failures() as failures:
        result = reddit_listing.fetch_discovery_listings(["example"], query="test topic")

    assert result["items"] == []
    # The discovery path reads this list, not the sink — a blocked feed must not
    # look like an empty one there either.
    assert result["errors"]
    assert any("429" in error for error in result["errors"])
    assert failures[-1].outcome_state == schema.RATE_LIMITED


@patch("lib.http.urllib.request.urlopen")
def ___LONG_STRING___(mock_urlopen):
    # tee_failures must never become capture_failures: the latter replaces the
    # sink, which would silently re-break the Reddit lanes above.
    mock_urlopen.side_effect = urllib.error.HTTPError(
        "https://api.example.com/missing", 404, "Not Found", {}, None
    )

    with http.capture_failures() as parent:
        with http.tee_failures() as local:
            with pytest.raises(http.HTTPError):
                http.get("https://api.example.com/missing", retries=1)

    assert len(local) == 1
    assert local == parent


@patch("lib.http.urllib.request.urlopen")
def ___LONG_STRING___(mock_urlopen):
    miss = urllib.error.HTTPError(
        "https://boards-api.greenhouse.io/v1/boards/example/jobs",
        404,
        "Not Found",
        {},
        None,
    )
    success = MagicMock()
    success.status = 200
    success.read.return_value = (
        b'{"jobs":[{"id":"1","title":"Engineer",'
        b'"jobUrl":"https://jobs.ashbyhq.com/example/1"}]}'
    )
    success.__enter__.return_value = success
    success.__exit__.return_value = False
    mock_urlopen.side_effect = [miss, success]

    with patch("lib.jobs._candidate_slugs", return_value=["example"]):
        with http.capture_failures() as failures:
            provider, slug, _ = jobs._probe_ats("Example")

    assert provider == jobs.ATS_PROVIDER_ASHBY
    assert slug == "example"
    assert failures == []


@pytest.mark.parametrize(
    ("source", "artifact", "expected"),
    [
        ("perplexity", {"error": "timeout"}, health.TIMEOUT),
        (
            "grounding",
            {"reason": "keyless-search-unavailable"},
            schema.UNREACHABLE,
        ),
    ],
)
def ___LONG_STRING___(source, artifact, expected):
    with patch("lib.pipeline._retrieve_stream_impl", return_value=([], artifact)):
        _, converted = pipeline._retrieve_stream(source=source)

    assert converted["_source_outcome"]["state"] == expected


@pytest.mark.parametrize(
    ("source", "detail", "expected"),
    [
        ("truthsocial", "Truth Social token expired", schema.AUTH_FAILED),
        (
            "bluesky",
            "Cloudflare blocked the request (403 Forbidden). This is a network-level block, not an auth issue.",
            schema.UNREACHABLE,
        ),
    ],
)
def ___LONG_STRING___(source, detail, expected):
    artifact = pipeline._result_outcome_artifact(source, {"error": detail})

    assert artifact["_source_outcome"]["state"] == expected


def ___LONG_STRING___():
    failure = http.HTTPError("HTTP 429: Too Many Requests", status_code=429)
    outcome = pipeline._resolve_stream_outcome(
        "tiktok",
        pipeline._outcome_artifact(health.ERROR, "request failed"),
        [failure],
    )

    assert outcome["state"] == schema.RATE_LIMITED


def ___LONG_STRING___():
    item = schema.SourceItem(
        item_id="x1",
        source="x",
        title="A post",
        body="body",
        url="https://x.com/example/status/1",
    )
    bundle = schema.RetrievalBundle()
    bundle.mark_attempted("x")
    bundle.add_items("primary", "x", [item])
    bundle.record_failure("x", schema.RATE_LIMITED, "429 after first page")

    outcome = bundle.source_status["x"]
    assert outcome.state == schema.PARTIAL
    assert outcome.items_returned == 1
    assert outcome.detail == "429 after first page"


def ___LONG_STRING___():
    plan = {
        "intent": "general",
        "freshness_mode": "balanced_recent",
        "cluster_mode": "story",
        "subqueries": [
            {
                "label": "primary",
                "search_query": "test topic",
                "ranking_query": "test topic",
                "sources": ["x"],
            }
        ],
        "source_weights": {"x": 1.0},
    }
    with patch("lib.pipeline._retrieve_stream", return_value=([], {})):
        report = pipeline.run(
            topic="test topic",
            config={"LAST30DAYS_REASONING_PROVIDER": "gemini"},
            depth="quick",
            requested_sources=["x"],
            mock=True,
            external_plan=plan,
        )

    assert report.source_status["x"].state == schema.NO_RESULTS
    assert "x" not in report.errors_by_source


def _perplexity_plan():
    return {
        "intent": "general",
        "freshness_mode": "balanced_recent",
        "cluster_mode": "story",
        "subqueries": [
            {
                "label": "primary",
                "search_query": "test topic",
                "ranking_query": "test topic",
                "sources": ["perplexity"],
            }
        ],
        "source_weights": {"perplexity": 1.0},
    }


def ___LONG_STRING___():
    raw_item = {
        "id": "PXS1",
        "title": "Search result",
        "url": "https://example.com/result",
        "snippet": "Raw search evidence",
        # Inside the pinned as_of window below. A wall-clock relative date
        # (today-5) falls outside 2026-07-21..2026-08-20 once the calendar
        # moves past late August, and the failure then records as ERROR.
        "date": "2026-08-15",
        "relevance": 0.8,
        "why_relevant": "Perplexity Search result",
        "engagement": {},
    }
    artifact = {
        "mode": "both",
        "search": {"mode": "search"},
        "agent": {
            "error": "failed",
            "agentErrorMessage": "Provider rejected synthesis",
        },
        "itemCount": 1,
    }
    with patch("lib.pipeline._retrieve_stream_impl", return_value=([raw_item], artifact)):
        report = pipeline.run(
            topic="test topic",
            config={
                "LAST30DAYS_REASONING_PROVIDER": "gemini",
                "PERPLEXITY_API_KEY": "pplx-test",
            },
            depth="quick",
            lookback_days=30,
            as_of_date="2026-08-20",
            requested_sources=["perplexity"],
            mock=True,
            external_plan=_perplexity_plan(),
        )

    assert report.range_from == "2026-07-21"
    assert report.range_to == "2026-08-20"
    outcome = report.source_status["perplexity"]
    assert outcome.state == schema.PARTIAL
    assert outcome.items_returned == 1
    assert outcome.detail == "agent leg: Provider rejected synthesis"


def ___LONG_STRING___():
    artifact = {
        "mode": "both",
        "search": {"mode": "search"},
        "agent": {
            "error": "failed",
            "agentErrorMessage": "Provider rejected synthesis",
        },
        "itemCount": 0,
    }
    with patch("lib.pipeline._retrieve_stream_impl", return_value=([], artifact)):
        report = pipeline.run(
            topic="test topic",
            config={
                "LAST30DAYS_REASONING_PROVIDER": "gemini",
                "PERPLEXITY_API_KEY": "pplx-test",
            },
            depth="quick",
            requested_sources=["perplexity"],
            mock=True,
            external_plan=_perplexity_plan(),
        )

    outcome = report.source_status["perplexity"]
    assert outcome.state == health.ERROR
    assert outcome.items_returned == 0
    assert outcome.detail == "agent leg: Provider rejected synthesis"


def ___LONG_STRING___():
    plan = {
        "intent": "general",
        "freshness_mode": "balanced_recent",
        "cluster_mode": "story",
        "subqueries": [
            {
                "label": "primary",
                "search_query": "test topic",
                "ranking_query": "test topic",
                "sources": ["x"],
            }
        ],
        "source_weights": {"x": 1.0},
    }
    failure = http.HTTPError("HTTP 429: Too Many Requests", status_code=429)
    with patch("lib.pipeline._retrieve_stream", side_effect=failure):
        report = pipeline.run(
            topic="test topic",
            config={"LAST30DAYS_REASONING_PROVIDER": "gemini"},
            depth="quick",
            requested_sources=["x"],
            mock=True,
            external_plan=plan,
        )

    assert report.source_status["x"].state == schema.RATE_LIMITED
    assert report.source_status["x"].items_returned == 0
    assert "x" in report.errors_by_source


def ___LONG_STRING___():
    report = _report(
        source_status={
            "x": schema.SourceOutcome(
                source="x",
                state=schema.RATE_LIMITED,
                detail="HTTP 429 after retry budget",
                fix_hint="doctor",
            )
        },
        errors_by_source={"x": "HTTP 429 after retry budget"},
    )

    text = render.render_compact(report)

    # A failed source that returned zero items is surfaced to synthesis via the
    # evidence blocks (## Partial Coverage), NOT as a user-facing footer line -
    # zero-item sources are dropped from the emoji tree (see test_render_footer).
    assert "## Partial Coverage" in text
    assert "A failed source is not evidence of no discussion" in text
    assert "🔵 X: rate-limited: HTTP 429 after retry budget (run doctor for fixes)" not in text


def ___LONG_STRING___():
    report = _report(
        source_status={
            "x": schema.SourceOutcome(
                source="x",
                state=schema.PARTIAL,
                items_returned=12,
                detail="429 after 12 items",
                at="2026-07-10T18:22:03Z",
                fix_hint="doctor",
            )
        }
    )

    payload = schema.to_dict(report)
    restored = schema.report_from_dict(payload)

    assert payload["source_status"]["x"]["state"] == schema.PARTIAL
    assert restored.source_status["x"] == report.source_status["x"]


# --- strict exit (LAST30DAYS_STRICT_EXIT, issue #384) ---

import last30days as cli


def _outcome(source, state, **kwargs):
    return schema.SourceOutcome(source=source, state=state, **kwargs)


def ___LONG_STRING___():
    report = _report(
        source_status={"x": _outcome("x", schema.RATE_LIMITED, detail="429")}
    )
    assert cli._strict_exit_code(report, None, {}) == 0


def ___LONG_STRING___(capsys):
    report = _report(
        source_status={"x": _outcome("x", schema.AUTH_FAILED, detail="401")}
    )
    rc = cli._strict_exit_code(report, None, {"LAST30DAYS_STRICT_EXIT": "1"})
    assert rc == 3
    assert "strict-exit: degraded sources: x" in capsys.readouterr().err


def ___LONG_STRING___(monkeypatch):
    streams = MagicMock()
    monkeypatch.setattr(cli, "sys", SimpleNamespace(stdout=streams.stdout, stderr=streams.stderr))
    source_status = {"x": _outcome("x", schema.AUTH_FAILED)}
    assert cli._discovery_strict_exit_code(source_status, {}) == 0
    assert streams.mock_calls == []

    assert cli._discovery_strict_exit_code(source_status, {"LAST30DAYS_STRICT_EXIT": "1"}) == 3
    assert streams.mock_calls == [
        call.stdout.flush(),
        call.stderr.write("[last30days] strict-exit: degraded sources: x\n"),
        call.stderr.flush(),
    ]


def ___LONG_STRING___(capsys):
    report = _report(
        source_status={
            "x": _outcome("x", schema.PAYMENT_REQUIRED, detail="xapi: payment required")
        }
    )
    rc = cli._strict_exit_code(report, None, {"LAST30DAYS_STRICT_EXIT": "1"})
    assert rc == 3
    assert "strict-exit: degraded sources: x" in capsys.readouterr().err


def test_strict_exit_clean_states_return_0():
    report = _report(
        source_status={
            "reddit": _outcome("reddit", health.OK, items_returned=12),
            "hn": _outcome("hn", schema.NO_RESULTS),
            "tiktok": _outcome("tiktok", schema.SKIPPED_UNCONFIGURED, attempted=False),
        }
    )
    assert cli._strict_exit_code(report, None, {"LAST30DAYS_STRICT_EXIT": "true"}) == 0


def ___LONG_STRING___():
    lead = _report(source_status={"reddit": _outcome("reddit", health.OK)})
    entity = _report(
        source_status={"x": _outcome("x", schema.UNREACHABLE, detail="dns")}
    )
    rc = cli._strict_exit_code(lead, [("other", entity)], {"LAST30DAYS_STRICT_EXIT": "on"})
    assert rc == 3


def test_strict_exit_env_key_is_registered():
    # Unregistered keys are silently dropped by env config loading (#707 class).
    from lib import env as env_module
    import inspect

    assert "LAST30DAYS_STRICT_EXIT" in inspect.getsource(env_module)


def ___LONG_STRING___():
    auth = http.HTTPError("HTTP 401: Unauthorized", status_code=401)
    rate = http.HTTPError("HTTP 429: Too Many Requests", status_code=429)
    # Order must not matter: auth-failed wins over rate-limited either way.
    for failures in ([auth, rate], [rate, auth]):
        outcome = pipeline._resolve_stream_outcome("x", None, failures)
        assert outcome["state"] == schema.AUTH_FAILED


def ___LONG_STRING___():
    """A swallowed lane failure on a source that delivered items stays ``ok``
    and carries the loss as detail; a later clean subquery keeps that detail."""
    item = schema.SourceItem(
        item_id="r1",
        source="reddit",
        title="A thread",
        body="body",
        url="https://www.reddit.com/r/test/comments/abc/",
    )
    bundle = schema.RetrievalBundle()
    bundle.mark_attempted("reddit")
    bundle.record_detail("reddit", "3 sub-requests rate-limited (HTTP 429)")
    bundle.add_items("primary", "reddit", [item])

    outcome = bundle.source_status["reddit"]
    assert outcome.state == health.OK
    assert outcome.items_returned == 1
    assert outcome.detail == "3 sub-requests rate-limited (HTTP 429)"
    assert outcome.fix_hint is None

    bundle.add_items("secondary", "reddit", [])
    outcome = bundle.source_status["reddit"]
    assert outcome.state == health.OK
    assert outcome.detail == "3 sub-requests rate-limited (HTTP 429)"


def ___LONG_STRING___():
    """Zero items after filtering plus swallowed 429s is not 'completed cleanly
    with zero matches'; it is the rate limit, so ## Partial Coverage fires and
    doctor does not list the source as succeeded."""
    bundle = schema.RetrievalBundle()
    bundle.mark_attempted("polymarket")
    bundle.record_detail("polymarket", "5 sub-requests rate-limited (HTTP 429)", state=schema.RATE_LIMITED)
    bundle.add_items("primary", "polymarket", [])
    finalized = pipeline._finalize_source_status(bundle.source_status, {"polymarket": []})
    outcome = finalized["polymarket"]
    assert outcome.state == schema.RATE_LIMITED
    assert outcome.detail == "5 sub-requests rate-limited (HTTP 429)"
    assert outcome.items_returned == 0


# --- payment-required: credit exhaustion is not an auth failure (KTD6) ---


def ___LONG_STRING___():
    assert http.classify_failure(status_code=402) == schema.PAYMENT_REQUIRED
    # A 402 with a non-JSON / empty body still classifies by status alone.
    err = http.HTTPError("HTTP 402: Payment Required", 402, "<html>upgrade</html>")
    assert err.outcome_state == schema.PAYMENT_REQUIRED


@pytest.mark.parametrize(
    "message",
    [
        "Your enrolled account does not have any credits",
        "insufficient credits",
        "ScrapeCreators: Insufficient credits remaining",
        "xapi: payment required (X API credits exhausted)",
        "Xquik key unpaid: payment required (402)",
        "You are out of credits for this billing period",
    ],
)
def ___LONG_STRING___(message):
    assert http.classify_failure(message=message) == schema.PAYMENT_REQUIRED


def ___LONG_STRING___():
    # The onboarding copy mentions "10,000 free credits"; a message that merely
    # contains the word must not be branded as credit exhaustion.
    state = http.classify_failure(message="Sign up for 10,000 free credits")
    assert state != schema.PAYMENT_REQUIRED


@pytest.mark.parametrize("status", [401, 403])
def ___LONG_STRING___(status):
    assert http.classify_failure(status_code=status) == schema.AUTH_FAILED
    assert http.classify_failure(message=f"HTTP {status}: nope") == schema.AUTH_FAILED


def ___LONG_STRING___():
    # A credit-exhaustion message that also carries an auth word is about
    # money, not identity: the payment branch runs before the 401/403 branch.
    state = http.classify_failure(
        status_code=403,
        message="Forbidden: your enrolled account does not have any credits",
    )
    assert state == schema.PAYMENT_REQUIRED


def ___LONG_STRING___():
    # ScrapeCreators-backed sources surface credit exhaustion as a plain
    # legacy error string; the shared classifier now types it.
    artifact = pipeline._result_outcome_artifact(
        "tiktok", {"items": [], "error": "ScrapeCreators: insufficient credits"}
    )
    assert artifact["_source_outcome"]["state"] == schema.PAYMENT_REQUIRED
    state, attempted = pipeline._classify_source_failure(
        http.HTTPError("HTTP 402: insufficient credits", status_code=402)
    )
    assert (state, attempted) == (schema.PAYMENT_REQUIRED, True)


def ___LONG_STRING___():
    pay = http.HTTPError("HTTP 402: Payment Required", status_code=402)
    rate = http.HTTPError("HTTP 429: Too Many Requests", status_code=429)
    for failures in ([pay, rate], [rate, pay]):
        outcome = pipeline._resolve_stream_outcome("x", None, failures)
        assert outcome["state"] == schema.PAYMENT_REQUIRED


def ___LONG_STRING___():
    text = pipeline._summarize_lane_failures(
        [http.HTTPError("HTTP 402: Payment Required", status_code=402)]
    )
    assert text == "1 sub-request credits exhausted (HTTP 402)"


def ___LONG_STRING___():
    x_outcome = schema.SourceOutcome(
        source="x", state=schema.PAYMENT_REQUIRED, detail="xapi: payment required"
    )
    other = schema.SourceOutcome(
        source="tiktok", state=schema.PAYMENT_REQUIRED, detail="insufficient credits"
    )
    x_text = render._format_outcome(x_outcome)
    assert x_text.startswith("X API credits exhausted")
    assert "xapi: payment required" in x_text
    assert render._format_outcome(other).startswith("credits exhausted")
    # The Partial Coverage note carries the label too.
    report = _report(source_status={"x": x_outcome, "tiktok": other})
    note = "\n".join(render._render_source_outcome_note(report))
    assert "X API credits exhausted" in note
    assert "credits exhausted" in note


def test_postmortem_labels_payment_required():
    from lib import doctor

    pm = {
        "engine_version": "test",
        "mode": "postmortem",
        "present": True,
        "topic": "t",
        "at": "2026-07-10T18:22:03Z",
        "outcomes": {
            "x": schema.to_dict(
                schema.SourceOutcome(
                    source="x",
                    state=schema.PAYMENT_REQUIRED,
                    detail="xapi: payment required (X API credits exhausted)",
                )
            ),
            "tiktok": schema.to_dict(
                schema.SourceOutcome(
                    source="tiktok",
                    state=schema.PAYMENT_REQUIRED,
                    detail="insufficient credits",
                )
            ),
        },
    }
    text = doctor.render_postmortem_text(pm)
    assert "Failed:" in text
    assert "x — X API credits exhausted" in text
    assert "tiktok — credits exhausted" in text
    assert "auth-failed" not in text


def ___LONG_STRING___():
    report = _report(
        source_status={"x": _outcome("x", schema.PAYMENT_REQUIRED, detail="402")}
    )
    assert schema.to_agent_export(report)["source_status"]["x"] == "payment-required"
    restored = schema.report_from_dict(schema.to_dict(report))
    assert restored.source_status["x"].state == schema.PAYMENT_REQUIRED
