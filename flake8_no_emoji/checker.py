from typing import Generator, Tuple, Type
from .categories import get_category
import emoji

class NoEmojiChecker:
    name = "flake8-no-emoji"
    version = "0.3.0"
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

        # ⚠️ Запрет одновременного использования
        if cls._ignore_categories & cls._only_categories:
            raise ValueError(
                f"Cannot use both --ignore-emoji-types={','.join(cls._ignore_categories)} "
                f"and --only-emoji-types={','.join(cls._only_categories)} at the same time."
            )

    def __init__(self, tree, filename: str = "stdin") -> None:
        self.filename = filename

    def run(self) -> Generator[Tuple[int, int, str, Type["NoEmojiChecker"]], None, None]:
        """Iterate file, detect emoji using categories, yield all emoji per line."""
        if self.filename == "stdin":
            return

        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except (OSError, UnicodeDecodeError):
            return

        only = getattr(self.__class__, "_only_categories", set())
        ignore = getattr(self.__class__, "_ignore_categories", set())

        for lineno, line in enumerate(lines, start=1):
            for idx, char in enumerate(line):
                if not char.strip():
                    continue  # skip whitespace/control chars
                if emoji.is_emoji(char):
                    category = get_category(char).upper()
                    # Only takes precedence
                    if only and category not in only:
                        continue
                    if ignore and category in ignore:
                        continue
                    yield lineno, idx, self._error_tmpl, type(self)
