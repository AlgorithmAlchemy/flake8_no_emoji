# tests/test_checker.py
import os
import tempfile

from flake8_no_emoji.checker import NoEmojiChecker


# Helper to create a temporary file with content
def make_temp_file(content):
    fd, path = tempfile.mkstemp(suffix=".py", text=True)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def test_detect_face_emoji():
    content = "print('Hello 😄')\n"
    path = make_temp_file(content)
    checker = NoEmojiChecker(None, path)
    results = list(checker.run())
    os.remove(path)
    assert len(results) == 1
    assert results[0][2] == "EMO001 Emoji detected in code"


def test_ignore_face_emoji():
    content = "print('Hello 😄')\n"
    path = make_temp_file(content)
    checker = NoEmojiChecker(None, path, ignore_emoji_types="FACE")
    results = list(checker.run())
    os.remove(path)
    assert results == []


def test_detect_animal_emoji():
    content = "print('Look at this 🐶')\n"
    path = make_temp_file(content)
    checker = NoEmojiChecker(None, path)
    results = list(checker.run())
    os.remove(path)
    assert len(results) == 1


def test_multiple_emojis():
    content = "print('😄🐶☀️')\n"
    path = make_temp_file(content)
    checker = NoEmojiChecker(None, path, ignore_emoji_types="ANIMAL")
    results = list(checker.run())
    os.remove(path)
    # FACE 😄 and SYMBOL ☀️ should be detected, ANIMAL 🐶 ignored
    assert len(results) == 1
