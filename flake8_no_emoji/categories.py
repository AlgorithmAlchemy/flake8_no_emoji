# flake8_no_emoji/categories.py
"""
Emoji categories defined by Unicode codepoint ranges.
We test codepoints in an emoji grapheme cluster and return the first matching category.
"""

from typing import List, Tuple

# Each category maps to list of (start, end) codepoint ranges (inclusive).
CATEGORIES: dict[str, List[Tuple[int, int]]] = {
    "PEOPLE": [
        (0x1F600, 0x1F64F),  # emoticons
        (0x1F466, 0x1F487),  # people & body
    ],
    "NATURE": [
        (0x1F300, 0x1F5FF),  # symbols & pictographs (many nature items too)
        (0x1F400, 0x1F4FF),  # animals & other pictographs
    ],
    "FOOD": [
        (0x1F32D, 0x1F37F),  # food & drink related
    ],
    "ACTIVITY": [
        (0x1F3A0, 0x1F3FF),  # activities
    ],
    "TRAVEL": [
        (0x1F680, 0x1F6FF),  # transport & map symbols
    ],
    "OBJECTS": [
        (0x1F4A0, 0x1F4FF),  # objects / office / tech
        (0x1F50A, 0x1F52F),
    ],
    "SYMBOLS": [
        (0x1F500, 0x1F5FF),
        (0x2600, 0x26FF),
        (0x2700, 0x27BF),  # dingbats
    ],
    "FLAGS": [
        (0x1F1E6, 0x1F1FF),  # regional indicator symbols (pairs form country flags)
    ],
    # add more categories/ranges if needed
}


def get_category(grapheme: str) -> str:
    """
    Return a category name for the given grapheme cluster.
    We check each codepoint in the cluster against defined ranges.
    Returns 'OTHER' if no range matches.
    """
    for cp in (ord(ch) for ch in grapheme):
        for category, ranges in CATEGORIES.items():
            for start, end in ranges:
                if start <= cp <= end:
                    return category
    return "OTHER"
