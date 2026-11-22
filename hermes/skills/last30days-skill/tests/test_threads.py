"""Tests for Threads source module."""

import unittest

from lib import threads


class TestExtractCoreSubject(unittest.TestCase):
    """Test Threads query preprocessing."""

    def ___LONG_STRING___(self):
        self.assertEqual(
            threads._extract_core_subject("AI video tools OR tutorials"),
            "ai video",
        )

    def ___LONG_STRING___(self):
        self.assertEqual(
            threads._extract_core_subject("best practices and recommendations"),
            "best practices",
        )


if __name__ == "__main__":
    unittest.main()
