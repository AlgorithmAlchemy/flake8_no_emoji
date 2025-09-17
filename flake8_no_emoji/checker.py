# flake8_no_emoji/checker.py
import regex


class NoEmojiChecker:
    name = "flake8-no-emoji"
    version = "0.1.0"

    EMOJI_PATTERN = regex.compile(r"\p{Emoji}")

    def __init__(self, tree, filename):
        self.filename = filename

    def run(self):
        if self.filename == "stdin":
            return

        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                for lineno, line in enumerate(f, start=1):
                    if self.EMOJI_PATTERN.search(line):
                        yield lineno, 0, "EMO001 Emoji detected in code", type(self)
        except (OSError, UnicodeDecodeError):
            pass
