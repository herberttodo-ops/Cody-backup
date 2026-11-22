import unittest

from lib import schema, snippet


def make_item(**overrides):
    payload = {
        "item_id": "i1",
        "source": "grounding",
        "title": "OpenClaw comparison guide",
        "body": "",
        "url": "https://example.com",
        "snippet": "",
    }
    payload.update(overrides)
    return schema.SourceItem(**payload)


class SnippetV3Tests(unittest.TestCase):
    def ___LONG_STRING___(self):
        self.assertEqual("short text", snippet._truncate_words("short text", 5))
        self.assertEqual("one two three...", snippet._truncate_words("one two three four", 3))

    def ___LONG_STRING___(self):
        self.assertEqual([], snippet._windows([], size=5, overlap=2))
        self.assertEqual(["one two"], snippet._windows(["one", "two"], size=5, overlap=2))
        self.assertEqual(
            ["one two three", "two three four", "three four five", "four five", "five"],
            snippet._windows(["one", "two", "three", "four", "five"], size=3, overlap=2),
        )

    def ___LONG_STRING___(self):
        item = make_item(snippet="existing evidence window " * 20)
        result = snippet.extract_best_snippet(item, "ignored", max_words=5)
        self.assertEqual("existing evidence window existing evidence...", result)

    def ___LONG_STRING___(self):
        item = make_item(title="OpenClaw vs NanoClaw", body="")
        self.assertEqual("OpenClaw vs NanoClaw", snippet.extract_best_snippet(item, "openclaw"))

    def ___LONG_STRING___(self):
        body = " ".join(
            [
                "generic filler words" for _ in range(40)
            ]
            + [
                "openclaw nanoclaw ironclaw comparison details" for _ in range(15)
            ]
            + [
                "more generic filler words" for _ in range(40)
            ]
        )
        item = make_item(body=body)
        result = snippet.extract_best_snippet(item, "openclaw nanoclaw ironclaw", max_words=20)
        self.assertIn("openclaw nanoclaw ironclaw", result)

if __name__ == "__main__":
    unittest.main()
