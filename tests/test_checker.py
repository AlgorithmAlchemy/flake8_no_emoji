# tests/test_checker.py
import os
import tempfile
from types import SimpleNamespace
import pytest

from flake8_no_emoji.checker import NoEmojiChecker
from flake8_no_emoji.categories import CATEGORIES

def run_checker_on_content(content, ignore_emoji_types=None, only_emoji_types=None):
    """Write content to temp file, set options, run checker, return results."""
    fd, path = tempfile.mkstemp(suffix=".py", text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)

        opts = SimpleNamespace(
            ignore_emoji_types=(ignore_emoji_types or ""),
            only_emoji_types=(only_emoji_types or ""),
        )
        NoEmojiChecker.parse_options(opts)
        checker = NoEmojiChecker(tree=None, filename=path)
        checker._ignore_categories = NoEmojiChecker._ignore_categories
        checker._only_categories = NoEmojiChecker._only_categories
        return list(checker.run())
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def test_detect_any_emoji_by_default():
    results = run_checker_on_content("x = '😀'")
    assert results, "Emoji should be detected by default"


def test_ignore_category_people():
    results = run_checker_on_content("x = '😀'", ignore_emoji_types="PEOPLE")
    assert results == [], "PEOPLE emojis should be ignored"


def test_only_category_animals():
    results = run_checker_on_content("x = '🐶'", only_emoji_types="NATURE")
    assert results, "ANIMAL/NATURE emoji should be detected when only=NATURE"

    results = run_checker_on_content("x = '😀'", only_emoji_types="NATURE")
    assert results == [], "PEOPLE emoji should not be detected when only=NATURE"


def test_only_takes_precedence_over_ignore():
    results = run_checker_on_content("x = '🐶 😀'", only_emoji_types="NATURE", ignore_emoji_types="NATURE")
    assert results, "only should take precedence over ignore"


def test_stdin_skips_check():
    checker = NoEmojiChecker(tree=None, filename="stdin")
    assert list(checker.run()) == []


def test_oserror_on_open(monkeypatch):
    def bad_open(*a, **k):
        raise OSError
    monkeypatch.setattr("builtins.open", bad_open)
    checker = NoEmojiChecker(tree=None, filename="fake_nonexistent.py")
    assert list(checker.run()) == []


def test_no_emoji_no_detection():
    results = run_checker_on_content("x = 'hello'")
    assert results == []


def test_add_options_registers():
    class DummyParser:
        def __init__(self):
            self.calls = []
        def add_option(self, *args, **kwargs):
            self.calls.append((args, kwargs))

    parser = DummyParser()
    NoEmojiChecker.add_options(parser)
    names = [args[0] if args else None for args, _ in parser.calls]
    assert "--ignore-emoji-types" in names
    assert "--only-emoji-types" in names


def test_mixed_content():
    content = "x='😀'\ny='🐶'\nz='⭐'"
    results = run_checker_on_content(content, ignore_emoji_types="PEOPLE")
    detected_chars = []
    for r in results:
        line = content.splitlines()[r[0]-1]
        detected_chars.append(line[r[1]])
    assert "😀" not in detected_chars
    assert "🐶" in detected_chars
    assert "⭐" in detected_chars


def test_multiple_emojis_in_line():
    content = "x='😀🐶⭐'"
    results = run_checker_on_content(content)
    assert len(results) == 3, "Should detect all emojis in line"


def test_empty_file():
    results = run_checker_on_content("")
    assert results == []


def test_only_whitespace_lines():
    results = run_checker_on_content("\n   \n\t\n")
    assert results == []


def test_unknown_emoji_category():
    content = "x='🛸'"  # assume maps to OTHER
    results = run_checker_on_content(content)
    assert results, "Unknown category emoji should be detected"


def test_emoji_positions():
    content = "a='😀'\nb='🐶'\nc='⭐'"
    results = run_checker_on_content(content)
    positions = [(r[0], r[1]) for r in results]
    assert positions == [(1, 3), (2, 3), (3, 3)]


def test_emoji_with_modifiers():
    content = "x='👩‍💻'"
    results = run_checker_on_content(content)
    assert results, "Emoji with modifier should be detected"