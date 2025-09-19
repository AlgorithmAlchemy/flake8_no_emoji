from typing import List, Tuple

# Emoji categories defined by Unicode codepoint ranges.
CATEGORIES: dict[str, List[Tuple[int, int]]] = {
    "PEOPLE": [
        (0x1F600, 0x1F64F),  # emoticons
        (0x1F466, 0x1F487),  # people & body
        (0x1F9D0, 0x1F9E6),  # additional people
    ],
    "NATURE": [
        (0x1F400, 0x1F4D3),  # animals & nature
        (0x1F300, 0x1F32F),  # weather, plants
    ],
    "FOOD": [
        (0x1F32D, 0x1F37F),
    ],
    "ACTIVITY": [
        (0x1F3A0, 0x1F3FF),
    ],
    "TRAVEL": [
        (0x1F680, 0x1F6FF),
    ],
    "OBJECTS": [
        (0x1F4A0, 0x1F4FF),
        (0x1F50A, 0x1F52F),
    ],
    "SYMBOLS": [
        (0x1F500, 0x1F5FF),
        (0x2600, 0x26FF),
        (0x2700, 0x27BF),
    ],
    "FLAGS": [
        (0x1F1E6, 0x1F1FF),
    ],
}

def get_category(grapheme: str) -> str:
    """Return a category name for the given emoji grapheme."""
    for cp in (ord(ch) for ch in grapheme):
        for category, ranges in CATEGORIES.items():
            for start, end in ranges:
                if start <= cp <= end:
                    return category
    return "OTHER"
