# flake8_no_emoji/checker.py
import regex

# Specific emoji categories
EMOJI_CATEGORIES = {
    "PEOPLE": r"[\U0001F466-\U0001F487\U0001F600-\U0001F64F]",
    "NATURE": r"[\U0001F300-\U0001F5FF\U0001F400-\U0001F43F]",
    "FOOD": r"[\U0001F34F-\U0001F37F]",
    "ACTIVITY": r"[\U0001F3A0-\U0001F3FF]",
    "TRAVEL": r"[\U0001F680-\U0001F6FF]",
    "OBJECTS": r"[\U0001F4A0-\U0001F4FF\U0001F50A-\U0001F52F]",
    "SYMBOLS": r"[\U0001F500-\U0001F5FF\u2600-\u26FF\u2700-\u27BF]",
    "FLAGS": r"[\U0001F1E6-\U0001F1FF]",
}


class NoEmojiChecker:
    name = "flake8-no-emoji"
    version = "0.4.0"

    def __init__(self, tree, filename, ignore_emoji_types=None, only_emoji_types=None):
        self.filename = filename
        self.ignore_categories = set(ignore_emoji_types.split(",")) if ignore_emoji_types else set()
        self.only_categories = set(only_emoji_types.split(",")) if only_emoji_types else set()

        # Base universal matcher (future-proof)
        self.base_pattern = r"\p{Emoji}"

        # Determine categories based on mode
        if self.only_categories:
            # Only include explicitly selected categories
            patterns = [pat for cat, pat in EMOJI_CATEGORIES.items() if cat in self.only_categories]
            self.emoji_pattern = regex.compile("|".join(patterns)) if patterns else regex.compile("$^")  # match nothing
        else:
            # Include everything except ignored categories
            patterns = [pat for cat, pat in EMOJI_CATEGORIES.items() if cat not in self.ignore_categories]
            if patterns:
                self.emoji_pattern = regex.compile(f"{self.base_pattern}|{'|'.join(patterns)}")
            else:
                self.emoji_pattern = regex.compile(self.base_pattern)

    @classmethod
    def add_options(cls, parser):
        parser.add_option(
            "--ignore-emoji-types",
            default="",
            parse_from_config=True,
            help="Comma-separated emoji categories to ignore (PEOPLE,NATURE,FOOD,ACTIVITY,TRAVEL,OBJECTS,SYMBOLS,FLAGS)"
        )
        parser.add_option(
            "--only-emoji-types",
            default="",
            parse_from_config=True,
            help="Comma-separated emoji categories to check exclusively (PEOPLE,NATURE,FOOD,ACTIVITY,TRAVEL,OBJECTS,SYMBOLS,FLAGS)"
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
