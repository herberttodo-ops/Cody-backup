"""What the patent lane makes of the lists: groups, counts, entries, index."""

from __future__ import annotations

import copy
from datetime import date

from lib import render
from tests.test_patents_client import (
    DETAILS,
    PDF,
    FakeUSPTO,
    guid_of,
    make_row,
    recorded,
    run,
)
from tests.test_render_patents import _report

ARTIFACT_KEYS = {
    "company", "company_via_person", "window", "groups", "other_names", "counts",
    "entries", "index", "partial", "status",
}
COUNT_KEYS = {
    "applications", "grants", "name_matched_applications", "name_matched_grants",
    "first_publications", "name_matched_first_publications", "continuing",
    "previously_published_grants", "designs", "other_kinds", "floor",
}
ENTRY_KEYS = [
    "guid", "number", "title", "url", "kind", "kind_code", "published", "filed",
    "earliest_priority", "cpc", "filed_as", "group_kind", "applicant_location",
    "abstract", "first_claim",
]
INDEX_KEYS = ["title", "url", "kind", "published", "cpc", "filed_as", "group_kind"]

# Filed 2026-01-15 (make_row's default) with a parent more than 13 months older.
CONTINUING = {"related": ["2023-02-01"]}


def numbers(items: list[dict]) -> list[str]:
    return [guid_of(item["url"]) for item in items]


# --- Apple, as recorded ___LONG_STRING___


def apple_lists() -> dict[str, list[dict]]:
    """The recorded Apple lists plus the stranger the full live list held."""
    stranger = make_row(
        "US-___ID___-A1", "2026-10-20", name="Deep Apple Therapeutics, Inc.", cpc="A61K31/00",
    )
    return {
        "US-PGPUB": recorded("Apple", "US-PGPUB") + [stranger],
        "USPAT": recorded("Apple", "USPAT"),
    }


def ___LONG_STRING___(monkeypatch):
    FakeUSPTO(lists=apple_lists()).install(monkeypatch)

    artifact = run({"company": "Apple Inc.", "company_via_person": 1})["artifact"]

    assert set(artifact) == ARTIFACT_KEYS
    assert artifact["company"] == "Apple Inc."
    assert artifact["company_via_person"] is True
    assert artifact["window"] == {"from": "2026-10-14", "to": "2026-11-13"}
    assert set(artifact["counts"]) == COUNT_KEYS
    assert artifact["partial"] is None
    assert artifact["status"] == "digest"
    assert len(artifact["entries"]) == 12
    assert len(artifact["index"]) == 30
    for entry in artifact["entries"]:
        assert list(entry) == ENTRY_KEYS
    for item in artifact["index"]:
        assert list(item) == INDEX_KEYS
        assert isinstance(item["cpc"], str)


def ___LONG_STRING___(monkeypatch):
    FakeUSPTO(lists=apple_lists()).install(monkeypatch)

    artifact = run()["artifact"]

    assert artifact["groups"] == [
        {"name": "Apple Inc.", "kind": "confirmed", "applications": 88, "grants": 88},
    ]
    assert artifact["other_names"] == [{"name": "Deep Apple Therapeutics, Inc.", "count": 1}]
    assert artifact["counts"]["applications"] == 88
    assert artifact["counts"]["grants"] == 88
    assert artifact["counts"]["name_matched_applications"] == 0
    shown = artifact["entries"] + artifact["index"]
    assert {item["filed_as"] for item in shown} == {"Apple Inc."}
    assert "___ID___" not in numbers(shown)


def ___LONG_STRING___(monkeypatch):
    lists = apple_lists()
    FakeUSPTO(lists=lists).install(monkeypatch)

    artifact = run()["artifact"]

    counts = artifact["counts"]
    # 88 applications: 61 first publications and 27 continuing. 88 grants:
    # 68 B2 and one continuing B1, 13 designs, 6 B1 with no earlier publication.
    assert counts["continuing"] == 27
    assert counts["previously_published_grants"] == 69
    assert counts["designs"] == 13
    assert counts["other_kinds"] == 0
    assert counts["first_publications"] == 67
    assert counts["floor"] is False
    continuing = {
        row["publicationReferenceDocumentNumber"]
        for row in lists["US-PGPUB"]
        if row["relatedApplFilingDate"]
        and (
            date.fromisoformat(row["applicationFilingDate"][0][:10])
            - date.fromisoformat(min(row["relatedApplFilingDate"])[:10])
        ).days > 396
    }
    assert len(continuing) == 27
    shown = set(numbers(artifact["entries"] + artifact["index"]))
    assert not shown & continuing
    # Recorded documents USPTO's own continuity data marks as continuations.
    assert not shown & {"___ID___", "___ID___", "___ID___", "___ID___"}


def test_an_entry_carries_the_recorded_text(monkeypatch):
    FakeUSPTO(lists=apple_lists()).install(monkeypatch)

    entry = run()["artifact"]["entries"][0]

    assert entry["guid"] == "US-___ID___-A1"
    assert entry["number"] == "___ID___"
    assert entry["title"] == "SPEECH PREDICTION BASED ON MOTION"
    assert entry["url"] == PDF + "___ID___"
    assert (entry["kind"], entry["kind_code"]) == ("application", "A1")
    assert entry["published"] == "2026-11-12"
    assert entry["filed"] == "2026-04-23"
    assert entry["earliest_priority"] == "2025-05-12"
    assert entry["cpc"] == ["G06F3/165", "G06F3/012", "G06F3/013", "G06F3/017", "G06F3/167"]
    assert (entry["filed_as"], entry["group_kind"]) == ("Apple Inc.", "confirmed")
    assert entry["applicant_location"] == "Cupertino, CA, US"
    assert entry["abstract"].startswith("Some examples of the disclosure are directed to")
    assert len(entry["abstract"]) <= 1000
    assert entry["first_claim"].startswith("1. A method comprising: at a first computer system")
    assert "an intention of the user to speak" in entry["first_claim"]
    assert len(entry["first_claim"]) <= 1200
    assert "<" not in entry["abstract"] + entry["first_claim"]


def ___LONG_STRING___(monkeypatch):
    row = make_row("US-12790001-B1", "2026-11-10", kind="B1")
    detail = {
        "abstractHtml": "<p>An&nbsp;&amp; abstract</p>\n " + "word " * 280,
        "claimsHtml": "<b>1</b>. A device " + "that works " * 200 + "<br /> <b>2</b>. Other.",
        "applicantName": ["Somebody Else LLC", "Apple Inc."],
        "applicantCity": ["Austin", "Cupertino"],
        "assigneeName": ["Somebody Else LLC", "APPLE INC."],
        "assigneeCity": ["Seoul", "Cupertino"],
        "assigneeState": ["N/A", "CA"],
        "assigneeCountry": ["KR", "US"],
        "cpcInventive": [f"G06F3/0{n} 20130101" for n in range(8)],
        "continuityData": ["us-provisional-application US 63000001 20250101\n<br />"],
    }
    FakeUSPTO(lists={"USPAT": [row]}, details={"US-12790001-B1": detail}).install(monkeypatch)

    [entry] = run()["artifact"]["entries"]

    assert entry["kind"] == "grant"
    assert entry["abstract"].startswith("An & abstract word word")
    # A 1,400-character abstract prints 1,000; a 2,000-character claim prints 1,200.
    assert 995 <= len(entry["abstract"]) <= 1000
    assert entry["first_claim"].startswith("1. A device that works")
    assert 1190 <= len(entry["first_claim"]) <= 1200
    assert entry["applicant_location"] == "Cupertino, CA, US"
    assert len(entry["cpc"]) == 5
    assert entry["cpc"][0] == "G06F3/00"


def ___LONG_STRING___(monkeypatch):
    rows = [
        make_row("US-___ID___-A1", "2026-11-05"),
        make_row("US-12790002-B1", "2026-11-03", kind="B1"),
    ]
    for row in rows:
        row["publicationReferenceDocumentNumber"] = None
    FakeUSPTO(lists={"US-PGPUB": rows[:1], "USPAT": rows[1:]}).install(monkeypatch)

    entries = run()["artifact"]["entries"]

    assert [(entry["number"], entry["url"]) for entry in entries] == [
        ("___ID___", PDF + "___ID___"),
        ("12790002", PDF + "12790002"),
    ]


def ___LONG_STRING___(monkeypatch):
    row = make_row("US-___ID___-A1", "2026-11-05", related=["2025-09-01"])
    row["priorityClaimsDate"] = ["2025-06-30T00:00:00Z", "2025-08-01T00:00:00Z"]
    bare = make_row("US-___ID___-A1", "2026-11-04")
    bare["applicationFilingDate"] = None
    FakeUSPTO(lists={"US-PGPUB": [row, bare]}).install(monkeypatch)

    first, second = run()["artifact"]["entries"]

    assert first["earliest_priority"] == "2025-06-30"
    assert (second["filed"], second["earliest_priority"]) == (None, None)


# --- kinds and counts ___LONG_STRING___


def ___LONG_STRING___(monkeypatch):
    # Filed more than three years after its parent application.
    [row] = [
        row for row in recorded("Figure AI", "US-PGPUB") if row["guid"] == "US-___ID___-A1"
    ]
    fake = FakeUSPTO(lists={"US-PGPUB": [row]}).install(monkeypatch)

    artifact = run({"company": "Figure AI"})["artifact"]

    assert artifact["status"] == "counts-only"
    assert artifact["entries"] == []
    assert artifact["index"] == []
    assert artifact["partial"] is None
    assert artifact["counts"]["continuing"] == 1
    assert artifact["counts"]["first_publications"] == 0
    assert artifact["groups"] == [
        {"name": "Figure AI Inc.", "kind": "confirmed", "applications": 1, "grants": 0},
    ]
    # Nothing to order and nothing to read: no baseline search, no detail call.
    assert [call["kind"] for call in fake.calls] == ["session", "search", "search"]


def ___LONG_STRING___(monkeypatch):
    FakeUSPTO(lists={"USPAT": recorded("Figure AI", "USPAT")}).install(monkeypatch)

    artifact = run({"company": "Figure AI"})["artifact"]

    assert artifact["status"] == "counts-only"
    assert artifact["counts"]["grants"] == 2
    assert artifact["counts"]["previously_published_grants"] == 2


def test_each_kind_lands_in_its_bucket(monkeypatch):
    applications = [
        make_row("US-___ID___-A1", "2026-11-05"),
        make_row("US-___ID___-A1", "2026-11-05", **CONTINUING),
        make_row("US-___ID___-A9", "2026-11-05", kind="A9"),
        # A parent 396 days before filing is not yet "more than 13 months".
        make_row("US-___ID___-A1", "2026-11-04", related=["2024-12-15"]),
        make_row("US-___ID___-A1", "2026-11-04", related=["2024-12-14"]),
    ]
    grants = [
        make_row("US-12790011-B1", "2026-11-03", kind="B1"),
        make_row("US-12790012-B1", "2026-11-03", kind="B1", **CONTINUING),
        make_row("US-12790013-B2", "2026-11-03", kind="B2"),
        make_row("US-D1150001-S", "2026-11-03", kind="S"),
        make_row("US-RE50001-E", "2026-11-03", kind="E"),
    ]
    FakeUSPTO(lists={"US-PGPUB": applications, "USPAT": grants}).install(monkeypatch)

    artifact = run()["artifact"]

    counts = artifact["counts"]
    assert counts["applications"] == 5
    assert counts["grants"] == 5
    assert counts["first_publications"] == 3
    assert counts["continuing"] == 2
    assert counts["previously_published_grants"] == 2
    assert counts["designs"] == 1
    assert counts["other_kinds"] == 2
    assert [entry["guid"] for entry in artifact["entries"]] == [
        "US-___ID___-A1", "US-___ID___-A1", "US-12790011-B1",
    ]
    assert artifact["index"] == []


def ___LONG_STRING___(monkeypatch):
    lists = apple_lists()
    grant = next(row for row in lists["USPAT"] if row["guid"] == "US-12792808-B1")
    grant["datePublished"] = "2026-11-13T00:00:00Z"  # newest, so it is read first
    detail = {
        **copy.deepcopy(DETAILS["US-12786790-B2"]),
        "guid": "US-12792808-B1",
        "continuityData": [
            "continuation parent-doc US 16904342 20200617 US 11500001 child-doc US 18000001\n<br />"
        ],
    }
    fake = FakeUSPTO(lists=lists, details={"US-12792808-B1": detail}).install(monkeypatch)

    artifact = run()["artifact"]

    fetched = fake.detail_guids()
    assert fetched[0] == "US-12792808-B1"
    assert len(fetched) == 13
    entries = [entry["guid"] for entry in artifact["entries"]]
    assert entries == fetched[1:]
    assert "12792808" not in numbers(artifact["index"])
    assert artifact["partial"] is None
    counts = artifact["counts"]
    assert counts["first_publications"] == 66
    # A continuing B1 is a grant of something already published, as at list level.
    assert counts["previously_published_grants"] == 70
    assert counts["continuing"] == 27


def ___LONG_STRING___(monkeypatch):
    forms = {
        "US-___ID___-A1": ["parent US continuation 17838218 20220612 GRANTED \n child US 1\n<br />"],
        "US-___ID___-A1": ["parent WO continuation PCT/JP2024/042963 20241204 PENDING \n child US 2"],
        "US-___ID___-A1": ["parent US continuation-in-part 17000001 20220101 PENDING"],
        "US-___ID___-A1": ["parent US division 17000002 20220101 GRANTED"],
        "US-___ID___-A1": ["divisional parent-doc US 17000003 20220101"],
        "US-___ID___-A1": ["us-provisional-application US 63804555 20250512\n<br />"],
        "US-___ID___-A1": [],
        "US-___ID___-A1": None,
    }
    rows = [make_row(guid, "2026-11-05") for guid in forms]
    details = {guid: {"abstractHtml": "x", "continuityData": data} for guid, data in forms.items()}
    FakeUSPTO(lists={"US-PGPUB": rows}, details=details).install(monkeypatch)

    artifact = run()["artifact"]

    assert [entry["guid"] for entry in artifact["entries"]] == [
        "US-___ID___-A1", "US-___ID___-A1", "US-___ID___-A1",
    ]
    assert artifact["counts"]["continuing"] == 5
    assert artifact["counts"]["first_publications"] == 3
    assert artifact["partial"] is None


def ___LONG_STRING___(monkeypatch):
    rows = [make_row(f"US-202603400{n:02d}-A1", f"2026-11-{12 - n // 4:02d}") for n in range(30)]
    continuing = {"abstractHtml": "x", "continuityData": ["parent US continuation 1 20200101"]}
    details = {row["guid"]: continuing for row in rows[:10]}
    fake = FakeUSPTO(lists={"US-PGPUB": rows}, details=details).install(monkeypatch)

    artifact = run()["artifact"]

    assert len(fake.of("detail")) == 18
    assert len(artifact["entries"]) == 8
    assert artifact["counts"]["continuing"] == 10
    assert artifact["counts"]["first_publications"] == 20
    assert artifact["partial"] == {"missing_text": 4}
    assert len(artifact["index"]) == 12


# --- groups ___LONG_STRING___


def ___LONG_STRING___(monkeypatch):
    FakeUSPTO().install(monkeypatch)

    artifact = run({"company": "Microsoft"})["artifact"]

    assert artifact["groups"] == [{
        "name": "Microsoft Technology Licensing, LLC", "kind": "confirmed",
        "applications": 25, "grants": 25,
    }]
    counts = artifact["counts"]
    assert (counts["applications"], counts["grants"]) == (25, 25)
    assert (counts["name_matched_applications"], counts["name_matched_grants"]) == (0, 0)
    # The 25 applications: 18 first publications and 7 continuing. The 25
    # grants are all B2, each the grant of an application published earlier.
    assert counts["first_publications"] == 18
    assert counts["name_matched_first_publications"] == 0
    assert (counts["continuing"], counts["previously_published_grants"]) == (7, 25)
    assert artifact["status"] == "digest"
    assert len(artifact["entries"]) == 12
    for item in artifact["entries"] + artifact["index"]:
        assert item["group_kind"] == "confirmed"
        assert item["filed_as"] == "Microsoft Technology Licensing, LLC"


def ___LONG_STRING___(monkeypatch):
    opco = "OpenAI OpCo, LLC"
    applications = [
        *[make_row(f"US-___ID___{n}-A1", "2026-11-05", name=opco) for n in range(3)],
        make_row("US-___ID___-A1", "2026-11-04", name=opco, **CONTINUING),
    ]
    grants = [make_row("US-12790041-B1", "2026-11-03", name=opco, kind="B1")]
    FakeUSPTO(lists={"US-PGPUB": applications, "USPAT": grants}).install(monkeypatch)

    artifact = run({"company": "OpenAI"})["artifact"]

    assert artifact["groups"] == [
        {"name": opco, "kind": "confirmed", "applications": 4, "grants": 1},
    ]
    report = _report(artifact, topic="OpenAI")
    assert render._patents_footer_line(report) == (
        "📜 Patents: 4 applications published │ 1 granted │ 4 first US publications"
    )
    block = "\n".join(render._patent_digest_block(report))
    assert "filed as OpenAI OpCo, LLC" in block
    assert "not verified" not in block and "confirmed" not in block.casefold()


BLOCK_IMAGING = "Block Imaging, Inc."


def ___LONG_STRING___(monkeypatch):
    applications = [
        make_row("US-___ID___-A1", "2026-11-06", name="Block, Inc."),
        *[make_row(f"US-___ID___{n}-A1", "2026-11-05", name=BLOCK_IMAGING) for n in range(5)],
        make_row("US-___ID___-A1", "2026-11-04", name=BLOCK_IMAGING, **CONTINUING),
        make_row("US-___ID___-A9", "2026-11-04", name=BLOCK_IMAGING, kind="A9"),
    ]
    grants = [
        make_row("US-12790021-B2", "2026-11-03", name=BLOCK_IMAGING, kind="B2"),
        make_row("US-D1150002-S", "2026-11-03", name=BLOCK_IMAGING, kind="S"),
    ]
    FakeUSPTO(lists={"US-PGPUB": applications, "USPAT": grants}).install(monkeypatch)

    artifact = run({"company": "Block"})["artifact"]

    assert artifact["groups"] == [
        {"name": "Block, Inc.", "kind": "confirmed", "applications": 1, "grants": 0},
        {"name": BLOCK_IMAGING, "kind": "name-matched", "applications": 7, "grants": 2},
    ]
    assert artifact["counts"] == {
        "applications": 1, "grants": 0,
        "name_matched_applications": 7, "name_matched_grants": 2,
        "first_publications": 1, "name_matched_first_publications": 5,
        "continuing": 0, "previously_published_grants": 0, "designs": 0, "other_kinds": 0,
        "floor": False,
    }
    # The entries still hold the name-matched filings, labelled.
    assert [entry["group_kind"] for entry in artifact["entries"]] == [
        "confirmed", *["name-matched"] * 5,
    ]


def ___LONG_STRING___(monkeypatch):
    applications = [
        make_row("US-___ID___-A1", "2026-11-06", name="Block, Inc."),
        make_row("US-___ID___-A1", "2026-11-06", name="Block, Inc."),
        make_row("US-___ID___-A1", "2026-11-05", name=BLOCK_IMAGING),
        make_row("US-___ID___-A1", "2026-11-05", name=BLOCK_IMAGING),
    ]
    grants = [make_row("US-12790031-B1", "2026-11-04", name=BLOCK_IMAGING, kind="B1")]
    continuing = {"abstractHtml": "x", "continuityData": ["parent US continuation 1 20200101"]}
    demoted = ["US-___ID___-A1", "US-___ID___-A1", "US-12790031-B1"]
    FakeUSPTO(
        lists={"US-PGPUB": applications, "USPAT": grants},
        details={guid: continuing for guid in demoted},
    ).install(monkeypatch)

    artifact = run({"company": "Block"})["artifact"]

    assert [entry["guid"] for entry in artifact["entries"]] == [
        "US-___ID___-A1", "US-___ID___-A1",
    ]
    counts = artifact["counts"]
    # Confirmed: two candidates, one found to be a continuation.
    assert (counts["first_publications"], counts["continuing"]) == (1, 1)
    # Name-matched: three candidates, two demoted, and neither joins a count
    # of the company's own filings.
    assert counts["name_matched_first_publications"] == 1
    assert counts["previously_published_grants"] == 0


def ___LONG_STRING___(monkeypatch):
    fake = FakeUSPTO().install(monkeypatch)
    company = {"company": "Alphabet Inc.", "company_names": ["Google", "Waymo"]}

    artifact = run(company)["artifact"]

    assert [call["query"] for call in fake.of("search")] == [
        '("alphabet" OR "google" OR "waymo").aanm. AND @pd>="20261014"<="20261113"',
        '("alphabet" OR "google" OR "waymo").asnm. AND @pd>="20261014"<="20261113"',
    ]
    assert artifact["company"] == "Alphabet Inc."
    assert artifact["groups"] == [
        {"name": "Google LLC", "kind": "confirmed", "applications": 25, "grants": 25},
        {"name": "Waymo LLC", "kind": "confirmed", "applications": 16, "grants": 23},
    ]
    assert artifact["counts"]["applications"] == 41
    assert {entry["filed_as"] for entry in artifact["entries"]} <= {"Google LLC", "Waymo LLC"}


def ___LONG_STRING___(monkeypatch):
    fake = FakeUSPTO().install(monkeypatch)
    company = {
        "company": "Apple Inc.",
        "company_names": ["Apple", "Apple Computer, Inc.", "Beats Electronics", "beats electronics llc", None]
        + [f"Unit {n}" for n in range(20)],
    }

    run(company)

    phrases = fake.of("search")[0]["query"].split(").aanm.")[0].lstrip("(").split(" OR ")
    assert phrases[:2] == ['"apple"', '"beats electronics"']
    assert len(phrases) == 1 + 12


def test_strangers_alone_are_the_none_state(monkeypatch):
    rows = [row for row in recorded("Block", "US-PGPUB") if row["applicantName"] == ["QUICK BLOCK LIMITED"]]
    rows += [make_row(f"US-___ID___{n}-A1", "2026-11-05", name="Chopping Block &amp; Co.") for n in range(3)]
    fake = FakeUSPTO(lists={"US-PGPUB": rows}).install(monkeypatch)

    result = run({"company": "Block"})

    assert result == {
        "state": "none",
        "other_names": [
            {"name": "Chopping Block & Co.", "count": 3},
            {"name": "QUICK BLOCK LIMITED", "count": 1},
        ],
    }
    assert [call["kind"] for call in fake.calls] == ["session", "search", "search"]


def ___LONG_STRING___(monkeypatch):
    FakeUSPTO().install(monkeypatch)

    assert run({"company": "Anthropic"}) == {"state": "none", "other_names": []}


def test_other_names_are_the_five_largest(monkeypatch):
    rows = [
        make_row(f"US-20260360{size}{n:02d}-A1", "2026-11-05", name=f"Big Apple Ventures {size}")
        for size in range(1, 8) for n in range(size)
    ]
    FakeUSPTO(lists={"US-PGPUB": rows}).install(monkeypatch)

    other = run()["other_names"]

    assert [item["count"] for item in other] == [7, 6, 5, 4, 3]
    assert other[0]["name"] == "Big Apple Ventures 7"


def ___LONG_STRING___(monkeypatch):
    FakeUSPTO().install(monkeypatch)
    company = {"company": "IBM", "company_names": ["International Business Machines"]}

    artifact = run(company)["artifact"]

    assert artifact["groups"] == [{
        "name": "International Business Machines Corporation", "kind": "confirmed",
        "applications": 25, "grants": 25,
    }]
    assert artifact["other_names"] == []
    assert {item["filed_as"] for item in artifact["entries"] + artifact["index"]} == {
        "International Business Machines Corporation",
    }


def ___LONG_STRING___(monkeypatch):
    rows = [
        make_row("US-___ID___-A1", "2026-11-06", name=["Apple Retail Holdings LLC", "Apple Inc."]),
        make_row("US-___ID___-A1", "2026-11-05", name="Apple Retail Holdings LLC"),
        make_row("US-___ID___-A1", "2026-11-04", name=["Stranger Ltd", "APPLE RETAIL HOLDINGS, LLC"]),
        make_row("US-___ID___-A1", "2026-11-03"),
    ]
    rows[3]["applicantName"] = "Apple Inc"  # a string, not a list
    rows.append(make_row("US-___ID___-A1", "2026-11-02", name=None))
    FakeUSPTO(lists={"US-PGPUB": rows}).install(monkeypatch)

    artifact = run()["artifact"]

    assert artifact["groups"] == [
        {"name": "Apple Inc.", "kind": "confirmed", "applications": 2, "grants": 0},
        {"name": "Apple Retail Holdings LLC", "kind": "name-matched", "applications": 2, "grants": 0},
    ]
    assert artifact["other_names"] == []
    assert artifact["counts"]["applications"] == 2
    assert artifact["counts"]["name_matched_applications"] == 2
    assert artifact["counts"]["first_publications"] == 2
    assert artifact["counts"]["name_matched_first_publications"] == 2
    assert [(entry["filed_as"], entry["group_kind"]) for entry in artifact["entries"]] == [
        ("Apple Inc.", "confirmed"),
        ("Apple Retail Holdings LLC", "name-matched"),
        ("Apple Retail Holdings LLC", "name-matched"),
        ("Apple Inc.", "confirmed"),
    ]


def ___LONG_STRING___(monkeypatch):
    rows = [make_row("US-___ID___-A1", "2026-11-05")]
    for size in range(1, 11):
        rows += [
            make_row(f"US-202603801{size:02d}{n}-A1", "2026-11-05", name=f"Apple Division {size} LLC")
            for n in range(size)
        ]
    FakeUSPTO(lists={"US-PGPUB": rows}).install(monkeypatch)

    artifact = run()["artifact"]

    assert [(group["name"], group["applications"]) for group in artifact["groups"]] == [
        ("Apple Inc.", 1),
        *[(f"Apple Division {size} LLC", size) for size in range(10, 3, -1)],
    ]
    assert artifact["counts"]["name_matched_applications"] == sum(range(4, 11))


def ___LONG_STRING___(monkeypatch):
    units = [f"Orchard Unit {n}" for n in range(1, 10)]
    rows = [make_row("US-___ID___-A1", "2026-11-05")]
    rows += [
        make_row(f"US-___ID___{n}-A1", "2026-11-05", name=f"{unit} LLC")
        for n, unit in enumerate(units)
    ]
    rows.append(make_row("US-___ID___-A1", "2026-11-05", name="Apple Retail Holdings LLC"))
    FakeUSPTO(lists={"US-PGPUB": rows}).install(monkeypatch)

    artifact = run({"company": "Apple Inc.", "company_names": units})["artifact"]

    confirmed = [group for group in artifact["groups"] if group["kind"] == "confirmed"]
    assert len(confirmed) == 10
    assert artifact["counts"]["applications"] == 10
    assert artifact["counts"]["first_publications"] == 10
    # With the confirmed names past the cap, no name-matched name is kept.
    assert [group["name"] for group in artifact["groups"] if group["kind"] != "confirmed"] == []


# --- which candidates get text ___LONG_STRING___


def window_rows() -> list[dict]:
    """Fourteen candidates in a common class, newest first, and an older one
    in a class the company has not filed in."""
    rows = [
        make_row(f"US-202603900{n:02d}-A1", f"2026-11-{12 - n // 2:02d}", cpc="G06F3/01;H04L9/32")
        for n in range(14)
    ]
    rows.append(make_row("US-___ID___-A1", "2026-10-15", cpc="A61B5/02;G06F3/01"))
    return rows


def baseline_rows(count: int) -> list[dict]:
    return [
        make_row(f"US-202503{n:05d}-A1", "2026-03-01", cpc="G06F3/01;G06F3/02;H04L9/32")
        for n in range(count)
    ]


def ___LONG_STRING___(monkeypatch):
    rows = window_rows()
    FakeUSPTO(lists={"US-PGPUB": rows}, baseline=baseline_rows(19)).install(monkeypatch)

    artifact = run()["artifact"]

    assert [entry["guid"] for entry in artifact["entries"]] == [row["guid"] for row in rows[:12]]
    assert numbers(artifact["index"]) == [row["guid"].split("-")[1] for row in rows[12:]]


def ___LONG_STRING___(monkeypatch):
    rows = window_rows()
    # A full baseline would put the unseen class first; this one takes 31 of
    # the lane's 90 seconds, past its own share of 30.
    fake = FakeUSPTO(
        lists={"US-PGPUB": rows}, baseline=baseline_rows(30), seconds={"baseline": 31.0},
    ).install(monkeypatch)

    artifact = run()["artifact"]

    assert len(fake.of("baseline")) == 1
    assert [entry["guid"] for entry in artifact["entries"]] == [row["guid"] for row in rows[:12]]
    assert all(entry["abstract"] and entry["first_claim"] for entry in artifact["entries"])
    assert artifact["partial"] is None


def ___LONG_STRING___(monkeypatch):
    rows = window_rows()
    FakeUSPTO(lists={"US-PGPUB": rows}, baseline=baseline_rows(30)).install(monkeypatch)

    artifact = run()["artifact"]

    assert [entry["guid"] for entry in artifact["entries"]] == [
        "US-___ID___-A1", *[row["guid"] for row in rows[:11]],
    ]
    assert artifact["entries"][0]["published"] == "2026-10-15"


def ___LONG_STRING___(monkeypatch):
    common = [
        make_row(f"US-202604000{n:02d}-A1", f"2026-11-{12 - n:02d}", cpc="G06F3/01") for n in range(10)
    ]
    unseen = [
        make_row(f"US-202604001{n:02d}-A1", f"2026-10-{24 - n:02d}", cpc=f"A61B5/{n:02d}") for n in range(8)
    ]
    # Seen once in the baseline: rarer than the common class, less rare than unseen.
    seldom = make_row("US-___ID___-A1", "2026-11-13", cpc="B60W30/00")
    baseline = baseline_rows(30) + [make_row("US-___ID___-A1", "2026-02-01", cpc="B60W10/00")]
    fake = FakeUSPTO(
        lists={"US-PGPUB": common + unseen + [seldom]}, baseline=baseline,
    ).install(monkeypatch)

    artifact = run()["artifact"]

    assert [entry["guid"] for entry in artifact["entries"]] == [
        *[row["guid"] for row in unseen[:6]],
        seldom["guid"],
        *[row["guid"] for row in common[:5]],
    ]
    assert len(fake.of("baseline")) == 1


def ___LONG_STRING___(monkeypatch):
    rows = window_rows()
    strangers = [
        make_row(f"US-202503{n:05d}-A1", "2026-03-01", name="Deep Apple Therapeutics, Inc.", cpc="A61B5/02")
        for n in range(100, 140)
    ]
    FakeUSPTO(lists={"US-PGPUB": rows}, baseline=baseline_rows(30) + strangers).install(monkeypatch)

    assert run()["artifact"]["entries"][0]["guid"] == "US-___ID___-A1"


# --- a slot for each confirmed filer other than the company's own name ------------


NVIDIA_CO = {"company": "NVIDIA Corporation", "company_names": ["Mellanox Technologies"]}


def own_rows(count: int, *, name: str = "NVIDIA Corporation") -> list[dict]:
    """The company's own filings, all newer than any subsidiary's."""
    return [
        make_row(f"US-2026041{n:04d}-A1", f"2026-11-{12 - n % 10:02d}", name=name, cpc="G06F3/01")
        for n in range(count)
    ]


def filer_rows(prefix: str, name: str, count: int) -> list[dict]:
    return [
        make_row(f"US-2026042{prefix}{n:02d}-A1", f"2026-10-{20 - n:02d}", name=name, cpc="G06F3/01")
        for n in range(count)
    ]


def filed_as(artifact: dict) -> list[str]:
    return [entry["filed_as"] for entry in artifact["entries"]]


def ___LONG_STRING___(monkeypatch):
    rows = own_rows(20)
    FakeUSPTO(lists={"US-PGPUB": rows}).install(monkeypatch)

    artifact = run(NVIDIA_CO)["artifact"]

    newest = sorted(rows, key=lambda row: row["datePublished"], reverse=True)
    assert [entry["guid"] for entry in artifact["entries"]] == [row["guid"] for row in newest[:12]]


def ___LONG_STRING___(monkeypatch):
    rows = own_rows(150) + filer_rows("10", "Mellanox Technologies, Ltd.", 4)
    fake = FakeUSPTO(lists={"US-PGPUB": rows}).install(monkeypatch)

    artifact = run(NVIDIA_CO)["artifact"]

    assert len(artifact["entries"]) == 12
    assert filed_as(artifact).count("Mellanox Technologies, Ltd.") == 1
    assert len(fake.of("detail")) <= 18


def ___LONG_STRING___(monkeypatch):
    names = [f"Subsidiary {letter} Inc." for letter in "ABCDE"]
    rows = own_rows(60)
    for n, name in enumerate(names):
        rows += filer_rows(f"{n}0", name, 2)
    FakeUSPTO(lists={"US-PGPUB": rows}).install(monkeypatch)

    artifact = run({"company": "NVIDIA Corporation", "company_names": names})["artifact"]

    others = [name for name in filed_as(artifact) if name != "NVIDIA Corporation"]
    assert len(artifact["entries"]) == 12
    assert len(others) == len(set(others)) == 3


def ___LONG_STRING___(monkeypatch):
    rows = own_rows(40) + filer_rows("20", "NVIDIA Networking Solutions Inc.", 3)
    FakeUSPTO(lists={"US-PGPUB": rows}).install(monkeypatch)

    artifact = run(NVIDIA_CO)["artifact"]

    assert "NVIDIA Networking Solutions Inc." not in filed_as(artifact)
    assert set(filed_as(artifact)) == {"NVIDIA Corporation"}


def ___LONG_STRING___(monkeypatch):
    mellanox = filer_rows("30", "Mellanox Technologies, Ltd.", 2)
    rows = own_rows(40) + mellanox
    continuing = {"abstractHtml": "x", "continuityData": ["parent US continuation 1 20200101"]}
    fake = FakeUSPTO(
        lists={"US-PGPUB": rows}, details={mellanox[0]["guid"]: continuing},
    ).install(monkeypatch)

    artifact = run(NVIDIA_CO)["artifact"]

    assert [entry["guid"] for entry in artifact["entries"] if entry["filed_as"] != "NVIDIA Corporation"] == [
        mellanox[1]["guid"],
    ]
    assert len(artifact["entries"]) == 12
    assert len(fake.of("detail")) <= 18


def ___LONG_STRING___():
    from collections import Counter

    from lib import patents

    def candidate(guid, published, key, cpc, other):
        return {"guid": guid, "published": published, "group_key": key, "cpc": [cpc], "other_filer": other}

    # Six rare parent filings, then six newer filings from subsidiary A fill
    # the twelve slots; subsidiary B's two older filings sit outside them.
    parent = [candidate(f"p{n}", f"2026-01-{n + 1:02d}", "parent", f"A0{n}B 1/00", False) for n in range(6)]
    first = [candidate(f"a{n}", f"2026-06-{n + 1:02d}", "sub-a", "G06F 1/00", True) for n in range(6)]
    second = [candidate(f"b{n}", f"2025-12-{n + 1:02d}", "sub-b", "G06F 1/00", True) for n in range(2)]
    frequencies = Counter({"G06F": 50})

    ordered, reserved = patents._order(parent + first + second, frequencies)

    slots = [item["group_key"] for item in ordered[:patents.DETAIL_SLOTS]]
    assert reserved == {"sub-a", "sub-b"}
    assert slots.count("sub-b") == 1 and slots.count("sub-a") == 5 and slots.count("parent") == 6
