import unittest

from lib import query


class QueryV3Tests(unittest.TestCase):
    def ___LONG_STRING___(self):
        result = query.extract_core_subject("What are the best Claude Code skills for startups?")
        self.assertEqual("claude code startups", result)

    def ___LONG_STRING___(self):
        result = query.extract_core_subject(
            "How to use Claude Code prompting techniques",
            strip_suffixes=True,
            max_words=2,
        )
        self.assertEqual("claude code", result)

    def ___LONG_STRING___(self):
        result = query.extract_core_subject("all tokens", noise=frozenset({"all", "tokens"}))
        self.assertEqual("all tokens", result)

    def ___LONG_STRING___(self):
        self.assertEqual("", query.extract_core_subject("   "))
        result = query.extract_core_subject(
            "OpenClaw release notes",
            noise=frozenset({"release"}),
            max_words=2,
        )
        self.assertEqual("openclaw notes", result)

    def ___LONG_STRING___(self):
        terms = query.extract_compound_terms("Best multi-agent patterns in Claude Code and React Native")
        self.assertIn("multi-agent", terms)
        self.assertIn("Claude Code", terms)
        self.assertIn("React Native", terms)

if __name__ == "__main__":
    unittest.main()
