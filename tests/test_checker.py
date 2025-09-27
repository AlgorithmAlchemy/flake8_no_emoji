# tests/test_checker.py
import os
import tempfile
import pytest
from types import SimpleNamespace

from flake8_no_emoji.checker import NoEmojiChecker


def run_checker_on_content(content, ignore_emoji_types=None, only_emoji_types=None, filename=None):
    """
    Write content to a temp file (if filename not provided), set options, run checker, return results.
    Allows passing a real file path for special cases like unreadable or binary files.
    """
    if filename is None:
        fd, path = tempfile.mkstemp(suffix=".py", text=True)
    else:
        path = filename

    try:
        if filename is None:
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
        if filename is None:
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
    # при конфликте ожидаем ValueError
    opts = SimpleNamespace(ignore_emoji_types="NATURE", only_emoji_types="NATURE")
    with pytest.raises(ValueError, match="Cannot use the same category"):
        NoEmojiChecker.parse_options(opts)


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
    detected_lines = [r[0] for r in results]
    assert 1 not in detected_lines, "😀 ignored"
    assert 2 in detected_lines, "🐶 detected"
    assert 3 in detected_lines, "⭐ detected"


def test_multiple_emojis_in_line():
    content = "x='😀🐶⭐'"
    results = run_checker_on_content(content)
    assert len(results) == 1, "Only first emoji in line should be detected"


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
    # только первые emoji в каждой строке
    assert positions == [(1, 3), (2, 3), (3, 3)]


def test_emoji_with_modifiers():
    content = "x='👩‍💻'"
    results = run_checker_on_content(content)
    assert len(results) == 1, "Emoji with modifier should be detected"


def test_many_emojis_in_one_line():
    content = "x='😀🐶⭐🛸👩‍💻🏳️‍🌈'"
    results = run_checker_on_content(content)
    assert len(results) == 1, "Only first emoji per line should be reported"


def test_emoji_in_comments_and_strings():
    content = """
# Comment with emoji 🚨
x = "String with emoji 🐶"
y = 'Another string 😎'
"""
    results = run_checker_on_content(content)
    lines = [r[0] for r in results]
    assert lines == [2, 3, 4], "Each line with emoji should be flagged once"


def test_emoji_with_skin_tone_modifiers():
    content = "x='👍🏽 ✋🏿 👋🏻'"
    results = run_checker_on_content(content)
    assert len(results) == 1, "Only first emoji per line should be detected"


def test_only_whitespace_and_non_emoji_chars():
    content = "   \t\nabc\n123\n"
    results = run_checker_on_content(content)
    assert results == [], "No emojis should be detected in lines with only whitespace or normal chars"


def test_detect_flags():
    content = "x='🇺🇸🇩🇪🇯🇵'"
    results = run_checker_on_content(content)
    assert len(results) == 1, "Only first flag emoji should be reported"


def test_emoji_at_start_and_end_of_line():
    content = "😀 start\nmiddle 🐶 end 🏆"
    results = run_checker_on_content(content)
    positions = [(r[0], r[1]) for r in results]
    # только первые emoji на каждой строке
    assert positions == [(1, 0), (2, 7)], "Only first emoji in each line should be detected"


def test_multiple_lines_with_only_emojis():
    content = "😀\n🐶\n⭐\n🛸\n👩‍💻"
    results = run_checker_on_content(content)
    assert len(results) == 5, "Each line with single emoji should be detected"


def test_empty_file():
    results = run_checker_on_content("")
    assert results == [], "Empty file should produce no results"


def test_empty_comment():
    results = run_checker_on_content("# ")
    assert results == [], "Empty comment should produce no results"


def test_unreadable_file(tmp_path):
    path = tmp_path / "unreadable.py"
    path.write_text("x = '😀'")
    os.chmod(path, 0)  # remove permissions
    results = run_checker_on_content("", filename=str(path))
    assert results == [], "Unreadable file should produce no results"
    os.chmod(path, 0o644)


def test_binary_file(tmp_path):
    path = tmp_path / "binary.bin"
    path.write_bytes(b"\x00\x01\x02\x03\x04")
    results = run_checker_on_content("", filename=str(path))
    assert results == [], "Binary file should produce no results"


def test_disable_all_checks():
    # simulate ignoring all categories
    results = run_checker_on_content("x = '😀🐶⭐'",
                                     ignore_emoji_types="PEOPLE,NATURE,FOOD,ACTIVITY,TRAVEL,OBJECTS,SYMBOLS,FLAGS,OTHER")
    assert results == [], "All emoji checks disabled should produce no results"


def test_non_english_with_noqa():
    content = "# Привет 🌸 # noqa"
    results = run_checker_on_content(content)
    assert results == [], "Line with # noqa should skip emoji check"


def test_comment_with_multiple_noqa():
    content = "# 🚀 test # noqa something else # noqa"
    results = run_checker_on_content(content)
    assert results == [], "Multiple # noqa should skip check"


def test_string_with_noqa():
    content = "x = '😀' # noqa"
    results = run_checker_on_content(content)
    assert results == [], "String with # noqa should skip check"


def test_emoji_in_multiline_string():
    content = '''x = """Line 1
🚀 Line 2
Line 3 🐶"""'''
    results = run_checker_on_content(content)
    assert len(results) == 2, "Should detect emoji in multiline strings"


def test_emoji_in_docstring():
    content = '''"""
This is a docstring with emoji 🌸
"""'''
    results = run_checker_on_content(content)
    assert len(results) == 1, "Should detect emoji in docstrings"


def test_emoji_in_variable_name():
    content = "😀 = 5"
    results = run_checker_on_content(content)
    assert results, "Should detect emoji in variable names"


def test_emoji_in_function_name():
    content = "def 🐶():\n    pass"
    results = run_checker_on_content(content)
    assert results, "Should detect emoji in function names"


def test_multiple_noqa_in_code():
    content = "# noqa 🚀\n😀 # noqa"
    results = run_checker_on_content(content)
    assert results == [], "Multiple # noqa should skip all checks"


def test_only_category_with_no_matches():
    results = run_checker_on_content("x = '😀🐶'", only_emoji_types="FLAGS")
    assert results == [], "No matches for only category should yield no results"


def test_ignore_category_with_all_matches():
    results = run_checker_on_content("x = '😀🐶⭐'", ignore_emoji_types="PEOPLE,NATURE,SYMBOLS")
    assert results == [], "Ignoring all categories with matches should yield no results"


def test_unicode_non_emoji_characters():
    content = "x = '© ™ ∑ √'"
    results = run_checker_on_content(content)
    assert results == [], "Unicode symbols that are not emojis should not be detected"


def test_emoji_with_combining_characters():
    content = "x = '🇺🇸‍👩‍🚀'"
    results = run_checker_on_content(content)
    assert results, "Emoji with combining characters should be detected"


def test_long_file_with_sparse_emojis(tmp_path):
    path = tmp_path / "long_file.py"
    lines = ["print('line {}')\n".format(i) for i in range(1000)]
    lines[500] = "print('🚀')\n"
    path.write_text("".join(lines), encoding="utf-8")
    results = run_checker_on_content("", filename=str(path))
    assert results, "Long file with sparse emoji should detect at least one"


def test_noqa_with_different_cases():
    content = "# NoQA 🚀\n😀 # NoQa"
    results = run_checker_on_content(content)
    assert results == [], "NoQA in different cases should still skip checks"


def test_multiple_emojis_with_noqa():
    content = "x = '😀🐶⭐' # noqa"
    results = run_checker_on_content(content)
    assert results == [], "Line with multiple emojis and noqa should skip all checks"


def test_comment_only_with_emoji():
    content = "# 🚀"
    results = run_checker_on_content(content)
    assert results, "Emoji in comment should be detected"


def test_comment_with_emoji_and_text():
    content = "# This is 🚀 a comment"
    results = run_checker_on_content(content)
    assert results, "Emoji in comment with text should be detected"


def test_long_line_with_multiple_emojis():
    content = "x = '😀🐶⭐🛸👩‍💻🏳️‍🌈' * 100"
    results = run_checker_on_content(content)
    assert len(results) == 1, "Only first emoji per line should be reported even for long lines"


def test_ignore_case_category_names():
    results = run_checker_on_content("x = '😀'", ignore_emoji_types="people")
    assert results == [], "Category ignoring should be case insensitive"


def test_only_case_category_names():
    results = run_checker_on_content("x = '🐶'", only_emoji_types="nature")
    assert results, "Category only check should be case insensitive"
