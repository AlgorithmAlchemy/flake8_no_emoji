# tests/test_checker.py
import tempfile
import builtins
import pytest
from flake8_no_emoji.checker import NoEmojiChecker
from flake8.options.manager import OptionManager


def run_checker_on_content(content, **kwargs):
    """Helper to run checker on a temporary file."""
    with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tmp:
        tmp.write(content)
        tmp.flush()
        checker = NoEmojiChecker(tree=None, filename=tmp.name, **kwargs)
        return list(checker.run())


def test_detect_any_emoji_by_default():
    results = run_checker_on_content("x = '😀'")
    assert results, "Emoji should be detected by default"
    assert results[0][2].startswith("EMO001")


def test_ignore_category_people():
    results = run_checker_on_content("x = '😀'", ignore_emoji_types="PEOPLE")
    assert results == [], "PEOPLE emojis should be ignored"


def test_only_category_animals():
    results = run_checker_on_content("x = '🐶'", only_emoji_types="ANIMAL")
    assert results, "ANIMAL emoji should be detected when only=ANIMAL"

    results = run_checker_on_content("x = '😀'", only_emoji_types="ANIMAL")
    assert results == [], "PEOPLE emoji should not be detected when only=ANIMAL"


def test_only_takes_precedence_over_ignore():
    results = run_checker_on_content(
        "x = '🐶 😀'", only_emoji_types="ANIMAL", ignore_emoji_types="ANIMAL"
    )
    # Because "only" wins, ANIMAL should still be detected
    assert results, "only should take precedence over ignore"
    assert "EMO001" in results[0][2]


def test_stdin_skips_check():
    checker = NoEmojiChecker(tree=None, filename="stdin")
    assert list(checker.run()) == []


def test_oserror_on_open(monkeypatch):
    def fake_open(*args, **kwargs):
        raise OSError("boom")
    monkeypatch.setattr(builtins, "open", fake_open)
    checker = NoEmojiChecker(tree=None, filename="fake.py")
    assert list(checker.run()) == []


def test_no_pattern_means_no_detection():
    checker = NoEmojiChecker(tree=None, filename="tmp.py", only_emoji_types="UNKNOWN")
    assert list(checker.run()) == []


def test_add_options_registers():
    parser = OptionManager(prog="flake8", version="1.0")
    NoEmojiChecker.add_options(parser)
    opts = [opt.long_option_name for opt in parser.options]
    assert "--ignore-emoji-types" in opts
    assert "--only-emoji-types" in opts
