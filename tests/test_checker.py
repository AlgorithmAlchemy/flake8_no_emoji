# tests/test_checker.py
import os
import tempfile
import builtins
import pytest
from types import SimpleNamespace

from flake8_no_emoji.checker import NoEmojiChecker


def run_checker_on_content(content, ignore_emoji_types=None, only_emoji_types=None):
    """Helper: write content to a temp file, set parser options via parse_options,
    run checker and return results. Ensures temp file is removed."""
    fd, path = tempfile.mkstemp(suffix=".py", text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)

        # Prepare options object expected by parse_options
        opts = SimpleNamespace(
            ignore_emoji_types=(ignore_emoji_types or ""),
            only_emoji_types=(only_emoji_types or ""),
        )
        # Feed options to checker class (the code under test should provide parse_options)
        if hasattr(NoEmojiChecker, "parse_options"):
            NoEmojiChecker.parse_options(opts)
        else:
            # backward compatibility: try to set class attrs directly (rare)
            NoEmojiChecker.ignore = [x.strip().upper() for x in opts.ignore_emoji_types.split(",") if x]
            NoEmojiChecker.only = [x.strip().upper() for x in opts.only_emoji_types.split(",") if x]

        checker = NoEmojiChecker(tree=None, filename=path)
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
    results = run_checker_on_content("x = '🐶'", only_emoji_types="ANIMAL")
    assert results, "ANIMAL emoji should be detected when only=ANIMAL"
    # PEOPLE should not be caught when only=ANIMAL
    results = run_checker_on_content("x = '😀'", only_emoji_types="ANIMAL")
    assert results == [], "PEOPLE emoji should not be detected when only=ANIMAL"


def test_only_takes_precedence_over_ignore():
    # only=ANIMAL should keep animal even if ignore also mentions it (only wins)
    results = run_checker_on_content("x = '🐶 😀'", only_emoji_types="ANIMAL", ignore_emoji_types="ANIMAL")
    assert results, "only should take precedence over ignore"


def test_stdin_skips_check():
    checker = NoEmojiChecker(tree=None, filename="stdin")
    assert list(checker.run()) == []


def test_oserror_on_open(monkeypatch):
    def bad_open(*a, **k):
        raise OSError

    monkeypatch.setattr(builtins, "open", bad_open)
    checker = NoEmojiChecker(tree=None, filename="fake_nonexistent.py")
    assert list(checker.run()) == []


def test_no_pattern_means_no_detection():
    results = run_checker_on_content("x = 'hello'")
    assert results == []


def test_add_options_registers():
    """Use DummyParser to avoid depending on flake8 OptionManager implementation/version."""
    class DummyParser:
        def __init__(self):
            self.calls = []

        def add_option(self, *args, **kwargs):
            # record first positional arg (option name) and kwargs
            self.calls.append((args, kwargs))

    parser = DummyParser()
    NoEmojiChecker.add_options(parser)

    names = [args[0] if args else None for args, _ in parser.calls]
    assert "--ignore-emoji-types" in names, "add_options should register --ignore-emoji-types"
    assert "--only-emoji-types" in names, "add_options should register --only-emoji-types"
