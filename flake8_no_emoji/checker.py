import re
import unicodedata
from typing import List, Tuple, Optional


class NoEmojiChecker:
    name = "flake8-no-emoji"
    version = "1.0"
    _error_tmpl = "EMO001 Emoji detected in code"

    emoji_pattern = re.compile(
        "["
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F680-\U0001F6FF"  # transport & map
        "\U0001F700-\U0001F77F"  # alchemical
        "\U0001F780-\U0001F7FF"  # geometric
        "\U0001F800-\U0001F8FF"  # arrows
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA00-\U0001FA6F"  # chess, dice, etc.
        "\U0001FA70-\U0001FAFF"  # symbols & pictographs ext-A
        "\U00002700-\U000027BF"  # dingbats
        "\U00002600-\U000026FF"  # misc symbols
        "]+",
        flags=re.UNICODE,
    )

    CATEGORY_MAP = {
        "PEOPLE": ["EMOTICONS", "SUPPLEMENTAL SYMBOLS AND PICTOGRAPHS"],
        "ANIMAL": ["ANIMALS & NATURE", "SUPPLEMENTAL SYMBOLS AND PICTOGRAPHS"],
        "SYMBOL": ["DINGBATS", "MISCELLANEOUS SYMBOLS"],
    }

    def __init__(self, tree, filename: str = "stdin"):
        self.filename = filename
        self.only: Optional[List[str]] = None
        self.ignore: Optional[List[str]] = None

    @classmethod
    def add_options(cls, parser):
        parser.add_option(
            "--ignore-emoji-types",
            default="",
            parse_from_config=True,
            help="Comma-separated categories of emojis to ignore",
        )
        parser.add_option(
            "--only-emoji-types",
            default="",
            parse_from_config=True,
            help="Comma-separated categories of emojis to allow detection for",
        )

    @classmethod
    def parse_options(cls, options):
        cls.ignore = [x.strip().upper() for x in options.ignore_emoji_types.split(",") if x]
        cls.only = [x.strip().upper() for x in options.only_emoji_types.split(",") if x]

    def run(self) -> List[Tuple[int, int, str, type]]:
        if self.filename == "stdin":
            return []

        try:
            with open(self.filename, encoding="utf-8") as f:
                code = f.read()
        except OSError:
            return []

        matches = []
        for match in self.emoji_pattern.finditer(code):
            emoji_char = match.group(0)
            category = self._get_category(emoji_char)

            if self.only:
                if category not in self.only:
                    continue
            elif self.ignore:
                if category in self.ignore:
                    continue

            line = code.count("\n", 0, match.start()) + 1
            col = match.start() - code.rfind("\n", 0, match.start()) - 1
            matches.append((line, col, self._error_tmpl, type(self)))
        return matches

    def _get_category(self, char: str) -> str:
        try:
            name = unicodedata.name(char)
        except ValueError:
            return "OTHER"

        name = name.upper()
        if "FACE" in name or "SMILE" in name or "HAND" in name or "PERSON" in name:
            return "PEOPLE"
        if "CAT" in name or "DOG" in name or "ANIMAL" in name:
            return "ANIMAL"
        if "SYMBOL" in name or "DINGBAT" in name or "STAR" in name:
            return "SYMBOL"
        return "OTHER"
