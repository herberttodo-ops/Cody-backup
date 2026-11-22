"""The Polymarket footer names a recurring series once.

The "Elon Musk" run of 2026-11-10 printed three brackets of one weekly
"how many tweets" series:

    Polymarket: 13 markets | Elon Musk post 260-279 tweets from Nov 6 to
    Nov 13, 2026 24%, Elon Musk post 280-299 tweets from Nov 10 to Nov 17,
    2026 12%, Elon Musk post 40-64 tweets from Nov 9 to Nov 11, 2026 64%

while markets on his net worth, a meeting with Putin and a return to the
administration were in the same run. The items below are the Polymarket
section of that run's saved file: titles, lead questions, prices and volumes.
"""

from lib import polymarket, render, schema

TOPIC = "Elon Musk"

# (event id, event title, headline question, price, volume)
SAVED = [
    ("1302903", "Elon Musk Net Worth on November 30?",
     "Will Elon Musk's net worth be between $800B and $900B on November 30?", 0.43, 8433.4),
    ("1305851", "Elon Musk # tweets November 6 - November 13, 2026?",
     "Will Elon Musk post 260-279 tweets from November 6 to November 13, 2026?", 0.24, 695083.2),
    ("1244070", "Elon Musk # tweets in November 2026?",
     "Will Elon Musk post 1000+ tweets in November 2026?", 0.82, 112594.7),
    ("1329688", "Elon Musk # tweets November 10 - November 17, 2026?",
     "Will Elon Musk post 280-299 tweets from November 10 to November 17, 2026?", 0.12, 253060.4),
    ("1354158", "Elon Musk # tweets November 13 - November 20, 2026?",
     "Will Elon Musk post 280-299 tweets from November 13 to November 20, 2026?", 0.12, 32535.5),
    ("1333415", "Elon Musk # tweets November 9 - November 11, 2026?",
     "Will Elon Musk post 40-64 tweets from November 9 to November 11, 2026?", 0.64, 217052.5),
    ("1280261", "Elon Musk meets with Putin by...?",
     "Elon Musk meets with Putin by December 31, 2026?", 0.093, 4153.9),
    ("1116368", "Elon Musk out as Project Meridian co-lead by January 27?",
     "Elon Musk out as Project Meridian co-lead by January 27?", 0.56, 0),
    ("149602", "Will Elon Musk rejoin the Trump Administration in 2026?",
     "Will Elon Musk rejoin the Trump Administration in 2026?", 0.038, 0),
    ("73198", "Will Elon Musk announce Presidential run before 2027?",
     "Will Elon Musk announce Presidential run before 2027?", 0.009, 0),
]


def _item(event_id, title, question, price, volume):
    return schema.SourceItem(
        item_id=event_id, source="polymarket", title=title, body="",
        url=f"https://polymarket.com/event/{event_id}",
        engagement={"volume": volume} if volume else {},
        metadata={"question": question, "headline": {"question": question, "price": price}},
    )


def _footer(rows, limit=3):
    return render._polymarket_top_markets([_item(*row) for row in rows], limit=limit, topic=TOPIC)


def ___LONG_STRING___():
    keys = {polymarket.series_key(title) for _id, title, *_ in SAVED if "# tweets" in title}

    assert keys == {"elon musk tweets"}


def ___LONG_STRING___():
    assert polymarket.is_count_series("Elon Musk # tweets November 6 - November 13, 2026?")
    assert polymarket.is_count_series("", "Will Elon Musk post 260-279 tweets from November 6?")
    assert not polymarket.is_count_series(
        "Elon Musk Net Worth on November 30?",
        "Will Elon Musk's net worth be between $800B and $900B on November 30?",
    )


def ___LONG_STRING___():
    lines = _footer(SAVED)

    assert len(lines) == 3
    assert not any("tweets" in line for line in lines)
    assert lines[0].startswith("Elon Musk's net worth between $800B and $900B")
    assert lines[1] == "Elon Musk meets with Putin by Dec 31, 2026 9.3%"


def ___LONG_STRING___():
    rows = [row for row in SAVED if "# tweets" in row[1]] + [SAVED[0]]

    lines = _footer(rows)

    assert len(lines) == 2
    assert "net worth" in lines[0]
    # The most traded bracket stands for the series.
    assert lines[1] == "Elon Musk post 260-279 tweets from Nov 6 to Nov 13, 2026 24%"


def ___LONG_STRING___():
    lines = _footer([row for row in SAVED if "# tweets" in row[1]])

    assert lines == ["Elon Musk post 260-279 tweets from Nov 6 to Nov 13, 2026 24%"]
