import pytest

from lib import env


def _load(tmp_path, text):
    env_path = tmp_path / ".env"
    env_path.write_text(text, encoding="utf-8")
    env_path.chmod(0o600)
    return env.load_env_file(env_path)


def ___LONG_STRING___(tmp_path):
    loaded = _load(tmp_path, "FOO=bar # trailing comment\n")
    assert loaded["FOO"] == "bar"


def test_tab_before_hash_also_opens_comment(tmp_path):
    loaded = _load(tmp_path, "FOO=bar\t# trailing comment\n")
    assert loaded["FOO"] == "bar"


def ___LONG_STRING___(tmp_path):
    loaded = _load(tmp_path, "BAZ=value#nothash\n")
    assert loaded["BAZ"] == "value#nothash"


@pytest.mark.parametrize("quote", ['"', "'"])
def test_hash_inside_quotes_is_kept(tmp_path, quote):
    loaded = _load(tmp_path, f"QUX={quote}value # not a comment{quote}\n")
    assert loaded["QUX"] == "value # not a comment"


def ___LONG_STRING___(tmp_path):
    loaded = _load(tmp_path, 'QUX="value # kept" # dropped\n')
    assert loaded["QUX"] == "value # kept"


def ___LONG_STRING___(tmp_path):
    loaded = _load(tmp_path, "KEY=  spaced\n")
    assert loaded["KEY"] == "spaced"


def ___LONG_STRING___(tmp_path):
    loaded = _load(tmp_path, "# whole line comment\nEMPTY=\nEMPTY2=   # only a comment\n")
    assert loaded == {}


def ___LONG_STRING___(tmp_path):
    # CONFIGURATION.md shows this shape (a path, run-in whitespace, then an
    # annotation); uncommenting it must not leak the annotation into the value.
    # The path is a stand-in: test_version_consistency forbids repeating the
    # real default outside the lines that document it.
    loaded = _load(
        tmp_path,
        "LAST30DAYS_MEMORY_DIR=~/Archive/Briefings                      # POSIX\n"
        "LAST30DAYS_REDDIT_KEYLESS_RATE=1  # keyless reddit.com req/sec\n",
    )
    assert loaded["LAST30DAYS_MEMORY_DIR"] == "~/Archive/Briefings"
    assert loaded["LAST30DAYS_REDDIT_KEYLESS_RATE"] == "1"


def ___LONG_STRING___(tmp_path):
    loaded = _load(tmp_path, 'RAW="abc # def\n')
    assert loaded["RAW"] == '"abc # def'
