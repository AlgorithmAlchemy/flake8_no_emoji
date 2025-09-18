import tempfile
import os
import pytest

from flake8_no_emoji.checker import NoEmojiChecker
from flake8.options.manager import OptionManager


def run_checker_on_content(content, ignore_emoji_types=None, only_emoji_types=None):
    # create dummy options object
    class DummyOptions:
        def __init__(self):
            self.ignore_emoji_types = ignore_emoji_types
            self.only_emoji_types = only_emoji_types

    options = DummyOptions()

    # write test file
    filename = "test_file.py"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    # init checker with options object
    checker = NoEmojiChecker(tree=None, filename=filename, options=options)
    return list(checker.run())


def test_detect_any_emoji_by_default():
    results = run_checker_on_content("x = '😀'")
    assert results, "Emoji should be detected by default"


def test_ignore_category_people():
    results = run_checker_on_content("x = '😀'", ignore_emoji_types="PEOPLE")
    assert results == [], "PEOPLE emojis should be ignored"


def test_only_category_animals():
    results = run_checker_on_content("x = '🐶'", only_emoji_types="ANIMAL")
    assert results, "ANIMAL emoji should be detected when only=ANIMAL"


def test_only_takes_precedence_over_ignore():
    results = run_checker_on_content("x = '🐶 😀'", only_emoji_types="ANIMAL", ignore_emoji_types="ANIMAL")
    assert results, "only should take precedence over ignore"


def test_stdin_skips_check():
    checker = NoEmojiChecker(tree=None, filename="stdin")
    assert list(checker.run()) == []


def test_oserror_on_open(monkeypatch):
    def bad_open(*a, **k):
        raise OSError

    monkeypatch.setattr("builtins.open", bad_open)
    checker = NoEmojiChecker(tree=None, filename="fake.py")
    assert list(checker.run()) == []


def test_no_pattern_means_no_detection():
    results = run_checker_on_content("x = 'hello'")
    assert results == []


def test_add_options_registers():
    parser = OptionManager("flake8", "1.0")
    NoEmojiChecker.add_options(parser)
    opts, _ = parser.parse_args(["--ignore-emoji-types=PEOPLE"])
    assert opts.ignore_emoji_types == "PEOPLE"
