# flake8_no_emoji/checker.py
import regex  # dependency: add "regex" to install_requires
from typing import Generator, Tuple, Type

from .categories import get_category


class NoEmojiChecker:
    name = "flake8-no-emoji"
    version = "0.1.0"
    _error_tmpl = "EMO001 Emoji detected in code"

    # We'll iterate over grapheme clusters (\X) and test whether cluster contains emoji property.
    GRAPHEME_RE = regex.compile(r"\X", flags=regex.VERSION1)

    @classmethod
    def add_options(cls, parser) -> None:
        parser.add_option(
            "--ignore-emoji-types",
            default="",
            parse_from_config=True,
            help="Comma-separated list of emoji categories to ignore (PEOPLE,NATURE,FOOD,...)",
        )
        parser.add_option(
            "--only-emoji-types",
            default="",
            parse_from_config=True,
            help="Comma-separated list of emoji categories to check exclusively (takes precedence over ignore).",
        )

    @classmethod
    def parse_options(cls, options) -> None:
        # store as class attributes (flake8 calls this once)
        cls._ignore_categories = {
            s.strip().upper() for s in getattr(options, "ignore_emoji_types", "").split(",") if s.strip()
        }
        cls._only_categories = {
            s.strip().upper() for s in getattr(options, "only_emoji_types", "").split(",") if s.strip()
        }

    def __init__(self, tree, filename: str = "stdin") -> None:
        # filename is provided by flake8; "stdin" indicates piped input
        self.filename = filename

    def run(self) -> Generator[Tuple[int, int, str, Type["NoEmojiChecker"]], None, None]:
        """
        Iterate over file lines, split into grapheme clusters, find emoji clusters,
        decide by categories (only / ignore), and yield flake8 errors.
        Column is 0-based.
        """
        if self.filename == "stdin":
            return

        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except (OSError, UnicodeDecodeError):
            return

        for lineno, line in enumerate(lines, start=1):
            for match in self.GRAPHEME_RE.finditer(line):
                grapheme = match.group(0)
                # quick test: does cluster contain an emoji codepoint?
                # regex property \p{Emoji} matches emoji codepoints; search inside cluster
                if not regex.search(r"\p{Emoji}", grapheme):
                    continue

                # Determine category by codepoint ranges
                category = get_category(grapheme).upper()

                # only takes precedence
                only = getattr(self.__class__, "_only_categories", set())
                ignore = getattr(self.__class__, "_ignore_categories", set())

                if only:
                    if category not in only:
                        continue
                elif ignore:
                    if category in ignore:
                        continue

                col = match.start()  # 0-based column (flake8 expects 0-based)
                yield lineno, col, self._error_tmpl, type(self)
