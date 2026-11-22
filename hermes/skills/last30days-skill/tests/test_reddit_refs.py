"""Canonical Reddit thread identity: every URL form of a thread maps to one ref."""

import pytest

from lib import reddit_refs


CANONICAL = "https://www.reddit.com/r/LocalLLaMA/comments/1abc2de/"


class TestCanonicalThread:
    @pytest.mark.parametrize("raw", [
        "https://www.reddit.com/r/LocalLLaMA/comments/1abc2de/some_title/",
        "https://old.reddit.com/r/LocalLLaMA/comments/1abc2de/some_title/",
        "https://new.reddit.com/r/LocalLLaMA/comments/1abc2de/some_title/",
        "https://np.reddit.com/r/LocalLLaMA/comments/1abc2de/some_title/",
        "https://m.reddit.com/r/LocalLLaMA/comments/1abc2de/some_title/",
        "https://sh.reddit.com/r/LocalLLaMA/comments/1abc2de/some_title/",
        "https://reddit.com/r/LocalLLaMA/comments/1abc2de/some_title",
        "http://www.reddit.com/r/LocalLLaMA/comments/1abc2de/",
        "https://www.reddit.com/r/LocalLLaMA/comments/1abc2de",
        "https://old.reddit.com/r/LocalLLaMA/comments/1abc2de/some_title/kx9y8z7/",
        "https://www.reddit.com/r/LocalLLaMA/comments/1abc2de/some_title/?utm_source=share",
        "www.reddit.com/r/LocalLLaMA/comments/1abc2de/some_title/",
    ])
    def ___LONG_STRING___(self, raw):
        ref = reddit_refs.canonical_thread(raw)
        assert ref is not None
        assert ref.post_id == "1abc2de"
        assert ref.subreddit == "LocalLLaMA"
        assert ref.url == CANONICAL

    @pytest.mark.parametrize("raw", [
        "https://redd.it/1abc2de",
        "https://www.reddit.com/comments/1abc2de/",
        "https://www.reddit.com/comments/1abc2de/some_title/",
        "1abc2de",
        "t3_1abc2de",
        "T3_1ABC2DE",
    ])
    def ___LONG_STRING___(self, raw):
        ref = reddit_refs.canonical_thread(raw)
        assert ref is not None
        assert ref.post_id == "1abc2de"
        assert ref.subreddit == ""
        assert ref.url == "https://www.reddit.com/comments/1abc2de/"

    @pytest.mark.parametrize("raw", [
        "https://www.reddit.com/r/LocalLLaMA/s/AbCdEf123",
        "https://www.google.com/url?q=https://www.reddit.com/r/LocalLLaMA/comments/1abc2de/",
        "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AbCdEf",
        "https://example.com/r/LocalLLaMA/comments/1abc2de/",
        "https://notreddit.com/r/LocalLLaMA/comments/1abc2de/",
        "https://www.reddit.com/r/LocalLLaMA/",
        "https://www.reddit.com/user/someone/",
        "https://www.reddit.com/r/LocalLLaMA/wiki/index",
        "https://i.redd.it/abc123.png",
        "",
        "not a url at all",
        "https://www.reddit.com/r/LocalLLaMA/comments/not_base36!/",
    ])
    def test_rejects_non_thread_urls(self, raw):
        assert reddit_refs.canonical_thread(raw) is None

    def ___LONG_STRING___(self):
        ref = reddit_refs.canonical_thread(CANONICAL)
        assert ref.provenance == set()
        assert ref.matched_comment is None

    def test_thread_key_is_shared_across_forms(self):
        keys = {
            reddit_refs.thread_key("https://old.reddit.com/r/LocalLLaMA/comments/1abc2de/x/k1/"),
            reddit_refs.thread_key("https://redd.it/1abc2de"),
            reddit_refs.thread_key(CANONICAL),
        }
        assert len(keys) == 1
        assert reddit_refs.thread_key("https://example.com/a") is None


class TestCommentUnion:
    def ___LONG_STRING___(self):
        mine = [{"id": "c1", "score": 40, "excerpt": "a"}]
        theirs = [
            {"id": "c1", "score": 41, "excerpt": "a"},
            {"url": "https://reddit.com/r/s/comments/1abc2de/t/c2/", "score": 90, "excerpt": "b"},
            {"id": "c3", "score": None, "score_pending": True, "excerpt": "c"},
        ]
        merged = reddit_refs.union_comments(mine, theirs)
        assert [reddit_refs.comment_key(c) for c in merged] == ["c2", "c1", "c3"]
