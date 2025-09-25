# flake8_no_emoji/checker.py
from typing import Generator, Tuple, Type
import emoji
import regex as re
from .categories import get_category


class NoEmojiChecker:
    name = "flake8_no_emoji"
    version = "0.2.5"
    _error_tmpl = "EMO001 Emoji detected in code"

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
        cls._ignore_categories = {
            s.strip().upper() for s in getattr(options, "ignore_emoji_types", "").split(",") if s.strip()
        }
        cls._only_categories = {
            s.strip().upper() for s in getattr(options, "only_emoji_types", "").split(",") if s.strip()
        }

        if cls._ignore_categories & cls._only_categories:
            raise ValueError(
                "Cannot use the same category in both --ignore-emoji-types and --only-emoji-types"
            )

    def __init__(self, tree, filename: str = "stdin") -> None:
        self.filename = filename

    def run(self) -> Generator[Tuple[int, int, str, Type["NoEmojiChecker"]], None, None]:
        if self.filename == "stdin":
            return

        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except (OSError, UnicodeDecodeError):
            return

        for lineno, line in enumerate(lines, start=1):
            # Use regex \X to get extended grapheme clusters
            for match in re.finditer(r"\X", line):
                grapheme = match.group()
                if emoji.is_emoji(grapheme):
                    category = get_category(grapheme).upper() if get_category else None
                    only = getattr(self.__class__, "_only_categories", set())
                    ignore = getattr(self.__class__, "_ignore_categories", set())

                    if only and category and category not in only:
                        continue
                    if ignore and category and category in ignore:
                        continue

                    yield lineno, match.start(), self._error_tmpl, type(self)
                    break   # stop after 1 match