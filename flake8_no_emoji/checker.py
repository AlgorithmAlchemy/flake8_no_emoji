# flake8_no_emoji/checker.py
import regex

# Emoji categories (example)
EMOJI_CATEGORIES = {
    "FACE": r"[\U0001F600-\U0001F64F]",  # faces
    "ANIMAL": r"[\U0001F400-\U0001F43F]",  # animals
    "SYMBOL": r"[\U00002600-\U000027BF]"  # symbols
}


class NoEmojiChecker:
    name = "flake8-no-emoji"
    version = "0.1.0"

    def __init__(self, tree, filename, ignore_emoji_types=None):
        self.filename = filename
        self.ignore_categories = set()
        if ignore_emoji_types:
            self.ignore_categories = set(ignore_emoji_types.split(","))

        # Compile combined pattern for categories not ignored
        patterns = [
            pat for cat, pat in EMOJI_CATEGORIES.items() if cat not in self.ignore_categories
        ]
        self.emoji_pattern = regex.compile("|".join(patterns)) if patterns else None

    @classmethod
    def add_options(cls, parser):
        parser.add_option(
            "--ignore-emoji-types",
            default="",
            parse_from_config=True,
            help="Comma-separated emoji categories to ignore (FACE, ANIMAL, SYMBOL)"
        )

    def run(self):
        if not self.emoji_pattern or self.filename == "stdin":
            return

        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                for lineno, line in enumerate(f, start=1):
                    if self.emoji_pattern.search(line):
                        yield lineno, 0, "EMO001 Emoji detected in code", type(self)
        except (OSError, UnicodeDecodeError):
            pass
