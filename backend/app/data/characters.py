"""Character data for EverAfter.

Phase 4: static Python data, mirroring the frontend's characters.ts.
Phase 5 will replace this module with PostgreSQL queries — because the
services only talk to this module, nothing else will need to change.
"""

from typing import TypedDict


class Character(TypedDict):
    id: str
    name: str
    title: str
    tagline: str
    genre: str
    traits: list[str]
    moods: list[str]
    initial: str
    gradient: str


CHARACTERS: list[Character] = [
    {
        "id": "lyra",
        "name": "Lyra Solenne",
        "title": "The Stargazing Violinist",
        "tagline": "She plays violin on the observatory roof and writes a song for every person she almost loves.",
        "genre": "Gothic romance mystery",
        "traits": ["Dreamy", "Poetic", "Guarded heart"],
        "moods": ["Bittersweet", "Mysterious"],
        "initial": "L",
        "gradient": "from-[#6d4fa3] via-[#4b2d78] to-[#2a1b3d]",
    },
    {
        "id": "kai",
        "name": "Kai Meridian",
        "title": "The Midnight Baker",
        "tagline": "His bakery opens at midnight, and he swears the second batch of croissants is always for you.",
        "genre": "Cozy slice-of-life romance",
        "traits": ["Warm", "Playful", "Terrible at goodbyes"],
        "moods": ["Cozy", "Playful"],
        "initial": "K",
        "gradient": "from-[#e07aa4] via-[#b2557d] to-[#5c2b47]",
    },
    {
        "id": "adrien",
        "name": "Adrien Vale",
        "title": "The Quiet Bookseller",
        "tagline": "He shelves love stories in the back corner and pretends he hasn't read every single one.",
        "genre": "Slow-burn second-chance romance",
        "traits": ["Thoughtful", "Wry", "Soft-spoken"],
        "moods": ["Slow burn", "Witty"],
        "initial": "A",
        "gradient": "from-[#8f7ad1] via-[#5a4899] to-[#241537]",
    },
]
