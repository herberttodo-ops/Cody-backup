"""The bounded lines of the patent evidence block, built from the lane's artifact."""

import copy

from lib import patent_digest, patents

PDF = "https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/"
OTHERS = "- Other filers with the company's name, not verified:"

# Trimmed from a live Nvidia run on 2026-11-13: two of its twelve entries and
# two of its forty index items, counts as returned.
NVIDIA = {
    "company": "Nvidia",
    "company_via_person": False,
    "window": {"from": "2026-10-14", "to": "2026-11-13"},
    "groups": [
        {"name": "NVIDIA Corporation", "kind": "confirmed", "applications": 160, "grants": 86},
        {"name": "NVIDIA Corparation", "kind": "name-matched", "applications": 0, "grants": 1},
    ],
    "other_names": [],
    "counts": {
        "applications": 160, "grants": 86,
        "name_matched_applications": 0, "name_matched_grants": 1,
        # The name-matched grant is a first publication (it is in the index),
        # so 97 of the 98 the run found sit under the confirmed name.
        "first_publications": 97, "name_matched_first_publications": 1,
        "continuing": 73, "previously_published_grants": 75,
        "designs": 1, "other_kinds": 0, "floor": False,
    },
    "entries": [
        {
            "guid": "US-___ID___-A1", "number": "___ID___",
            "title": "DYNAMICALLY UPDATABLE PERSISTENT DISPLAYS FOR HARDWARE RESOURCES",
            "url": f"{PDF}___ID___", "kind": "application", "kind_code": "A1",
            "published": "2026-10-15", "filed": "2025-04-15", "earliest_priority": None,
            "cpc": ["G09G3/344", "G09G3/3453", "G09G3/035"],
            "filed_as": "NVIDIA Corporation", "group_kind": "confirmed",
            "applicant_location": "Santa Clara, CA, US",
            "abstract": (
                "Persistent displays such as E-ink persistent displays can convey information "
                "related to hardware components such as servers, GPUs, and network switches."
            ),
            "first_claim": (
                "1. A display device, comprising: a persistent display; a data connection to "
                "receive state data from a hardware device with which the persistent display "
                "is associated."
            ),
        },
        {
            "guid": "US-___ID___-A1", "number": "___ID___",
            "title": "TARGET OBJECT AND FEATURE MINING",
            "url": f"{PDF}___ID___", "kind": "application", "kind_code": "A1",
            "published": "2026-10-15", "filed": "2025-06-30", "earliest_priority": "2025-04-10",
            "cpc": ["B60W60/0027", "G08G1/0133"],
            "filed_as": "NVIDIA Corporation", "group_kind": "confirmed",
            "applicant_location": "Santa Clara, CA, US",
            "abstract": "Autonomous and/or semi-autonomous machine performance benefits from learning.",
            "first_claim": "1. A method comprising: receiving first data describing agent trajectories.",
        },
    ],
    "index": [
        {
            "title": "COMPILER-SCHEDULED TRIANGULAR UPDATE NEURAL NETWORK",
            "url": f"{PDF}___ID___", "kind": "application", "published": "2026-11-12",
            "cpc": "G06N3/08", "filed_as": "NVIDIA Corporation", "group_kind": "confirmed",
        },
        {
            "title": "TRIANGULAR UPDATE NEURAL NETWORK",
            "url": f"{PDF}___ID___", "kind": "grant", "published": "2026-11-12",
            "cpc": "G06N3/084; G06N3/048", "filed_as": "NVIDIA Corparation",
            "group_kind": "name-matched",
        },
    ],
    "partial": None,
    "status": "digest",
}


def _entry(number, *, filed_as="Microsoft Corporation", group_kind="confirmed", **fields):
    return {
        "guid": f"US-{number}-A1", "number": str(number), "title": f"Filing {number}",
        "url": f"{PDF}{number}", "kind": "application", "kind_code": "A1",
        "published": "2026-11-05", "filed": "2025-05-01", "earliest_priority": None,
        "cpc": ["G06F9/50"], "filed_as": filed_as, "group_kind": group_kind,
        "applicant_location": "Redmond, WA, US",
        "abstract": f"Abstract of {number}.", "first_claim": f"1. Claim of {number}.",
        **fields,
    }


def microsoft():
    licensing = "Microsoft Mobile Oy"
    return {
        "company": "Microsoft",
        "company_via_person": False,
        "window": {"from": "2026-10-14", "to": "2026-11-13"},
        "groups": [
            {"name": "Microsoft Corporation", "kind": "confirmed", "applications": 0, "grants": 1},
            {"name": licensing, "kind": "name-matched", "applications": 212, "grants": 140},
        ],
        "other_names": [{"name": "Nuance Communications, Inc.", "count": 3}],
        "counts": {
            "applications": 0, "grants": 1,
            "name_matched_applications": 212, "name_matched_grants": 140,
            # One entry below is filed under the confirmed name, two are not.
            "first_publications": 1, "name_matched_first_publications": 2,
            "continuing": 0, "previously_published_grants": 0,
            "designs": 0, "other_kinds": 0, "floor": False,
        },
        "entries": [
            _entry(1001, filed_as=licensing, group_kind="name-matched"),
            _entry(1002, kind="grant", kind_code="B1"),
            _entry(1003, filed_as=licensing, group_kind="name-matched"),
        ],
        "index": [],
        "partial": None,
        "status": "digest",
    }


def block():
    """One application under the company's own name and five under a
    stranger's that extends it."""
    imaging = "Block Imaging, Inc."
    return {
        "company": "Block",
        "company_via_person": False,
        "window": {"from": "2026-10-14", "to": "2026-11-13"},
        "groups": [
            {"name": "Block, Inc.", "kind": "confirmed", "applications": 1, "grants": 0},
            {"name": imaging, "kind": "name-matched", "applications": 5, "grants": 0},
        ],
        "other_names": [],
        "counts": {
            "applications": 1, "grants": 0,
            "name_matched_applications": 5, "name_matched_grants": 0,
            "first_publications": 1, "name_matched_first_publications": 5,
            "continuing": 0, "previously_published_grants": 0,
            "designs": 0, "other_kinds": 0, "floor": False,
        },
        "entries": [
            _entry(3001, filed_as="Block, Inc."),
            *[_entry(3002 + n, filed_as=imaging, group_kind="name-matched") for n in range(5)],
        ],
        "index": [],
        "partial": None,
        "status": "digest",
    }


def block_imaging_only():
    """Block with every filing under a stranger's name that extends it."""
    artifact = block()
    artifact["groups"] = artifact["groups"][1:]
    artifact["counts"].update(applications=0, first_publications=0)
    artifact["entries"] = [
        entry for entry in artifact["entries"] if entry["group_kind"] == "name-matched"
    ]
    return artifact


def openai_opco():
    """OpenAI with every filing under its operating company's name, which the
    lane counts as the company's own."""
    return {
        "company": "OpenAI",
        "company_via_person": False,
        "window": {"from": "2026-10-14", "to": "2026-11-13"},
        "groups": [
            {"name": "OpenAI OpCo, LLC", "kind": "confirmed", "applications": 14, "grants": 3},
        ],
        "other_names": [],
        "counts": {
            "applications": 14, "grants": 3,
            "name_matched_applications": 0, "name_matched_grants": 0,
            "first_publications": 15, "name_matched_first_publications": 0,
            "continuing": 2, "previously_published_grants": 0,
            "designs": 0, "other_kinds": 0, "floor": False,
        },
        "entries": [_entry(4001, filed_as="OpenAI OpCo, LLC")],
        "index": [],
        "partial": None,
        "status": "digest",
    }


def _link(url, title):
    return f"[{title}]({url})"


def _untrusted(text, limit):
    return text[:limit]


def lines(artifact):
    return patent_digest.digest_lines(artifact, link=_link, untrusted=_untrusted)


def _line(out, label):
    found = [line for line in out if line.startswith(label)]
    assert len(found) == 1, (label, out)
    return found[0]


def ___LONG_STRING___():
    artifact = copy.deepcopy(NVIDIA)
    artifact["other_names"] = [{"name": "Mellanox Technologies, Ltd.", "count": 4}]
    out = lines(artifact)
    assert out[:2] == ["## Patent Digest", ""]
    labels = [
        "- Filings:", OTHERS, "- First US publications:",
        "- [DYNAMICALLY UPDATABLE", "- [TARGET OBJECT",
        "- More first US publications (titles only):",
        "  - [COMPILER-SCHEDULED", "  - [TRIANGULAR UPDATE",
        "- Other names in the search, not read:",
    ]
    positions = [out.index(_line(out, label)) for label in labels]
    assert positions == sorted(positions)
    assert positions[-1] == len(out) - 1
    assert not any(line.startswith("- Note:") for line in out)


def ___LONG_STRING___():
    filings = _line(lines(NVIDIA), "- Filings:")
    assert "Nvidia" in filings
    assert "2026-10-14 to 2026-11-13" in filings
    assert "160 applications published" in filings
    assert "86 patents granted" in filings
    assert "NVIDIA Corporation" in filings
    assert "Corparation" not in filings


def ___LONG_STRING___():
    first = _line(lines(NVIDIA), "- First US publications:")
    assert first.startswith("- First US publications: 97 (")
    assert "73 continuing applications (continuations, divisionals)" in first
    assert "75 grants of applications published earlier" in first
    assert "1 design patent" in first
    assert "other kind" not in first


def ___LONG_STRING___():
    out = lines(NVIDIA)
    first = _line(out, "- [DYNAMICALLY UPDATABLE")
    assert first.startswith(
        "- [DYNAMICALLY UPDATABLE PERSISTENT DISPLAYS FOR HARDWARE RESOURCES]"
        f"({PDF}___ID___) | application ___ID___ | published 2026-10-15 | "
        "filed 2025-04-15 | CPC G09G3/344; G09G3/3453; G09G3/035 | "
        "filed as NVIDIA Corporation (Santa Clara, CA, US) | abstract: Persistent displays"
    )
    assert "earliest priority" not in first
    assert " | first claim: 1. A display device, comprising" in first
    assert "not verified" not in first
    second = _line(out, "- [TARGET OBJECT")
    assert "| filed 2025-06-30 | earliest priority 2025-04-10 | CPC" in second


def ___LONG_STRING___():
    artifact = microsoft()
    artifact["entries"] = [_entry(1, earliest_priority="2025-05-01")]
    assert "earliest priority" not in _line(lines(artifact), "- [Filing 1]")


def ___LONG_STRING___():
    out = lines(NVIDIA)
    assert _line(out, "  - [COMPILER-SCHEDULED") == (
        f"  - [COMPILER-SCHEDULED TRIANGULAR UPDATE NEURAL NETWORK]({PDF}___ID___) | "
        "application | published 2026-11-12 | CPC G06N3/08 | filed as NVIDIA Corporation"
    )
    assert _line(out, "  - [TRIANGULAR UPDATE").endswith(
        "| grant | published 2026-11-12 | CPC G06N3/084; G06N3/048 | "
        "filed as NVIDIA Corparation | not verified"
    )


def ___LONG_STRING___():
    out = lines(microsoft())
    order = [line.split("]")[0] for line in out if line.startswith("- [Filing")]
    assert order == ["- [Filing 1002", "- [Filing 1001", "- [Filing 1003"]
    confirmed = _line(out, "- [Filing 1002]")
    assert "| grant 1002 |" in confirmed
    assert "not verified" not in confirmed
    matched = _line(out, "- [Filing 1001]")
    assert (
        "| filed as Microsoft Mobile Oy (Redmond, WA, US) | not verified | "
        "abstract:" in matched
    )


def ___LONG_STRING___():
    out = lines(microsoft())
    filings = _line(out, "- Filings:")
    assert "0 applications published" in filings and "1 patent granted" in filings
    assert "212" not in filings and "140" not in filings and "Mobile" not in filings
    assert "Microsoft Corporation" in filings
    assert _line(out, OTHERS) == (
        f"{OTHERS} Microsoft Mobile Oy (212 applications, 140 grants); "
        "2 first US publications among them"
    )


def ___LONG_STRING___():
    out = lines(block())
    filings = _line(out, "- Filings:")
    assert "1 application published | 0 patents granted | filed as Block, Inc." in filings
    assert _line(out, "- First US publications:").startswith("- First US publications: 1 (")
    assert _line(out, OTHERS).endswith(
        "Block Imaging, Inc. (5 applications, 0 grants); 5 first US publications among them"
    )
    # The name-matched filings are still listed, labelled.
    listed = [line for line in out if line.startswith("- [Filing")]
    assert [("not verified" in line) for line in listed] == [False] + [True] * 5


def ___LONG_STRING___():
    assert _line(lines(NVIDIA), OTHERS).endswith(
        "NVIDIA Corparation (0 applications, 1 grant); 1 first US publication among them"
    )


def ___LONG_STRING___():
    artifact = block()
    artifact["counts"]["name_matched_first_publications"] = 0
    assert _line(lines(artifact), OTHERS).endswith(
        "Block Imaging, Inc. (5 applications, 0 grants)"
    )


def ___LONG_STRING___():
    out = lines(block_imaging_only())
    assert _line(out, "- Filings:") == (
        "- Filings: Block | US patent filings published 2026-10-14 to 2026-11-13 | "
        "none filed under the company's own name"
    )
    assert not any(line.startswith("- First US publications:") for line in out)
    assert _line(out, OTHERS).endswith(
        "Block Imaging, Inc. (5 applications, 0 grants); 5 first US publications among them"
    )
    listed = [line for line in out if line.startswith("- [Filing")]
    assert len(listed) == 5 and all("| not verified |" in line for line in listed)


def ___LONG_STRING___():
    out = lines(openai_opco())
    assert _line(out, "- Filings:").endswith(
        "| 14 applications published | 3 patents granted | filed as OpenAI OpCo, LLC"
    )
    assert _line(out, "- First US publications:").startswith("- First US publications: 15 (")
    assert not any(line.startswith(OTHERS) for line in out)
    assert "not verified" not in _line(out, "- [Filing 4001]")


def ___LONG_STRING___():
    artifact = copy.deepcopy(NVIDIA)
    artifact["groups"] = artifact["groups"][:1]
    assert not any(line.startswith(OTHERS) for line in lines(artifact))


def ___LONG_STRING___():
    assert _line(lines(microsoft()), "- Other names in the search, not read:") == (
        "- Other names in the search, not read: Nuance Communications, Inc. (3)"
    )


def test_floor_puts_a_plus_on_the_counts():
    artifact = microsoft()
    artifact["counts"]["floor"] = True
    out = lines(artifact)
    filings = _line(out, "- Filings:")
    assert "0+ applications published" in filings and "1+ patents granted" in filings
    assert _line(out, OTHERS).endswith(
        "(212+ applications, 140+ grants); 2+ first US publications among them"
    )
    assert _line(out, "- First US publications:").startswith("- First US publications: 1+ (")


def ___LONG_STRING___():
    artifact = copy.deepcopy(NVIDIA)
    artifact["company_via_person"] = True
    filings = _line(lines(artifact), "- Filings:")
    assert "Nvidia, the company the person leads" in filings
    assert "the company's filings, not the person's" in filings


def ___LONG_STRING___():
    artifact = copy.deepcopy(NVIDIA)
    artifact["partial"] = {"missing_text": 3}
    note = _line(lines(artifact), "- Note:")
    assert "3 of the filings listed by title only" in note
    assert "no abstract or claim text" in note
    assert "did not return it or time ran out" in note
    out = lines(artifact)
    assert out.index(_line(out, "- First US publications:")) + 1 == out.index(note)


def _full_size(entries, index=40):
    artifact = copy.deepcopy(NVIDIA)
    artifact["entries"] = [
        _entry(
            2000 + n, title="T" * 120, filed_as="NVIDIA Corporation",
            cpc=["G06N3/0455"] * patents.MAX_CPC_CODES, earliest_priority="2024-01-01",
            abstract="a" * patents.ABSTRACT_CHARS, first_claim="c" * patents.FIRST_CLAIM_CHARS,
        )
        for n in range(entries)
    ]
    artifact["index"] = [
        {**NVIDIA["index"][0], "title": f"Index {n} " + "T" * 120} for n in range(index)
    ]
    return artifact


def _size(out):
    return sum(len(line) + 1 for line in out)


def ___LONG_STRING___():
    out = lines(_full_size(entries=30, index=10))
    assert _size(out) <= patent_digest.DIGEST_MAX_CHARS == 36_000
    shown = sum(1 for line in out if line.startswith("- [T"))
    assert 0 < shown < 30
    note = _line(out, "- Note:")
    assert f"{30 - shown} entries and 10 titles left out" in note
    assert "36,000 characters" in note
    assert not any(line.startswith("- More first US publications") for line in out)
    assert not any(line.startswith("  - [") for line in out)


def ___LONG_STRING___():
    # Every slot filled with text at its own cap, and the whole index.
    assert (patents.ABSTRACT_CHARS, patents.FIRST_CLAIM_CHARS) == (1000, 1200)
    out = lines(_full_size(entries=patents.DETAIL_SLOTS, index=patents.MAX_INDEX))
    assert _size(out) <= patent_digest.DIGEST_MAX_CHARS
    assert sum(1 for line in out if line.startswith("- [T")) == patents.DETAIL_SLOTS


def ___LONG_STRING___():
    artifact = _full_size(entries=patents.DETAIL_SLOTS, index=patents.MAX_INDEX)
    for item in artifact["index"]:
        item["title"] = "T" * 400
    out = lines(artifact)
    assert _size(out) <= patent_digest.DIGEST_MAX_CHARS
    shown = sum(1 for line in out if line.startswith("  - ["))
    assert 0 < shown < patents.MAX_INDEX
    assert f"{patents.MAX_INDEX - shown} titles left out" in _line(out, "- Note:")


def ___LONG_STRING___():
    counts_only = copy.deepcopy(NVIDIA)
    counts_only.update(status="counts-only", entries=[], index=[])
    assert lines(counts_only) == []
    assert lines(None) == []
    assert lines({"status": "digest"}) == []
