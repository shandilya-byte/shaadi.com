"""Story data for EverAfter.

Phase 4: the "Rain, Again" story graph, ported from the frontend's
alex-cafe.ts. Same node ids, same choice ids, same variable effects —
so the two stay in sync until the backend becomes the single source
of truth. Phase 5 will move this into PostgreSQL.
"""

from typing import TypedDict

STARTING_VARS: dict[str, int] = {
    "trust": 0,
    "playfulness": 0,
    "openness": 0,
}


class Effects(TypedDict, total=False):
    trust: int
    playfulness: int
    openness: int


class StoryLine(TypedDict):
    speaker: str
    text: str


class StoryChoice(TypedDict):
    id: str
    label: str
    effects: Effects
    next: str


class StoryNode(TypedDict):
    id: str
    chapter: int
    title: str
    narration: list[str]
    lines: list[StoryLine]
    choices: list[StoryChoice]
    ending: str | None  # ending name on final nodes, else None


class Story(TypedDict):
    id: str
    title: str
    character_name: str
    character_initial: str
    gradient: str
    total_chapters: int
    start_node: str
    nodes: dict[str, StoryNode]


_st = StoryNode  # short alias to keep the graph readable


def _sl(**kwargs: str) -> StoryLine:  # noqa: N802 (small builder helpers)
    return StoryLine(**kwargs)


def _ch(**kwargs: object) -> StoryChoice:
    return StoryChoice(**kwargs)  # type: ignore[arg-type]


STORIES: dict[str, Story] = {
    "alex-cafe": {
        "id": "alex-cafe",
        "title": "Rain, Again",
        "character_name": "Alex",
        "character_initial": "A",
        "gradient": "from-[#7fb0c9] via-[#4f6d94] to-[#241537]",
        "total_chapters": 3,
        "start_node": "start",
        "nodes": {
            # ── Chapter 1 ──────────────────────────────────────
            "start": _st(
                id="start",
                chapter=1,
                title="The Café on Wren Lane",
                narration=[
                    "Rain writes long grey sentences down the windows of the café on Wren Lane. You duck inside, coat half-soaked, and the door chimes behind you like it is glad you came.",
                    "Then you see them at the corner table — the same warm eyes, the same half-smile from that afternoon you have replayed too many times. Alex stands, almost knocking over their cup.",
                ],
                lines=[
                    _sl(speaker="Alex", text="I've been hoping to see you again."),
                ],
                choices=[
                    _ch(
                        id="start-a",
                        label="Respond playfully — “Careful. That sounded like a confession.”",
                        effects=Effects(playfulness=2),
                        next="playful",
                    ),
                    _ch(
                        id="start-b",
                        label="Respond shyly — “I wasn't sure you'd remember me.”",
                        effects=Effects(trust=1, openness=1),
                        next="shy",
                    ),
                    _ch(
                        id="start-c",
                        label="Ask an emotional question — “Why were you hoping?”",
                        effects=Effects(openness=2),
                        next="question",
                    ),
                ],
                ending=None,
            ),
            # ── Chapter 2, path A: playful ─────────────────────
            "playful": _st(
                id="playful",
                chapter=2,
                title="The Tease",
                narration=[
                    "Alex laughs — surprised, then delighted. It is the kind of laugh they will deny making.",
                ],
                lines=[
                    _sl(speaker="Alex", text="Careful yourself. I collect people who flirt in thunderstorms."),
                    _sl(speaker="Alex", text="There are three others in this café alone."),
                    _sl(speaker="You", text="Liar. The rain would have told me."),
                ],
                choices=[
                    _ch(
                        id="playful-a",
                        label="Challenge them — “Prove it. Loser buys the coffee.”",
                        effects=Effects(playfulness=3),
                        next="ending-pact",
                    ),
                    _ch(
                        id="playful-b",
                        label="Drop the joke — “Honestly? The joke was a shield.”",
                        effects=Effects(openness=2, trust=1),
                        next="ending-warm",
                    ),
                ],
                ending=None,
            ),
            # ── Chapter 2, path B: shy ─────────────────────────
            "shy": _st(
                id="shy",
                chapter=2,
                title="The Soft Answer",
                narration=[
                    "Alex's expression gentles, like a light turned down on purpose. They slide the little menu across the table toward you, closer than it needs to be.",
                ],
                lines=[
                    _sl(speaker="Alex", text="I remember everything about that afternoon. It's slightly embarrassing."),
                    _sl(speaker="Alex", text="You ordered the lavender latte and apologized to the chair when you bumped it."),
                    _sl(speaker="You", text="The chair forgave me."),
                ],
                choices=[
                    _ch(
                        id="shy-a",
                        label="Compliment them — “You have a really good memory for small things.”",
                        effects=Effects(trust=2),
                        next="ending-window",
                    ),
                    _ch(
                        id="shy-b",
                        label="Confess — “I almost didn't come in today.”",
                        effects=Effects(openness=3),
                        next="ending-warm",
                    ),
                ],
                ending=None,
            ),
            # ── Chapter 2, path C: the question ────────────────
            "question": _st(
                id="question",
                chapter=2,
                title="The Real Question",
                narration=[
                    "The café noise seems to step back. Alex looks at you for a long moment, deciding something. Outside, the rain thickens.",
                ],
                lines=[
                    _sl(speaker="Alex", text="Because I walked past this café eleven times in two weeks."),
                    _sl(speaker="Alex", text="And because hope is embarrassing, and I'm doing it anyway."),
                ],
                choices=[
                    _ch(
                        id="question-a",
                        label="Go deeper — “What have you been afraid of?”",
                        effects=Effects(openness=2, trust=1),
                        next="ending-rain",
                    ),
                    _ch(
                        id="question-b",
                        label="Match their honesty — “So was I. Hoping, I mean.”",
                        effects=Effects(trust=2, openness=1),
                        next="ending-warm",
                    ),
                ],
                ending=None,
            ),
            # ── Chapter 3, endings ─────────────────────────────
            "ending-pact": _st(
                id="ending-pact",
                chapter=3,
                title="The Thunderstorm Pact",
                narration=[
                    "Alex loses the coffee-off on purpose — you both know it — and pays anyway, sliding the cup across like a treaty. On the napkin they've written a time and tomorrow's date.",
                    "“Same storm, same table,” they say, pulling their jacket over their head and stepping into the rain like it owes them money. You look at the napkin. You are absolutely coming back.",
                ],
                lines=[],
                choices=[],
                ending="The Thunderstorm Pact",
            ),
            "ending-window": _st(
                id="ending-window",
                chapter=3,
                title="The Window Seat",
                narration=[
                    "Alex reads your compliment twice, ears going pink, and then quietly moves to the window seat — the good one, the one regulars never give up — and pats the chair across from them.",
                    "The rain keeps writing its grey sentences. But now there are two cups on the table, and neither of you is in any hurry to finish them.",
                ],
                lines=[],
                choices=[],
                ending="The Window Seat",
            ),
            "ending-rain": _st(
                id="ending-rain",
                chapter=3,
                title="The Rain Does Not Ask",
                narration=[
                    "“Being wrong about someone,” Alex says slowly. “I've been wrong before. You spend two weeks hoping and then you watch a stranger drink their coffee and leave, and you learn to stop hoping so loud.”",
                    "You tell them you hope loudly too. Something in their shoulders lets go. The rain does not ask anything of either of you for a long, easy while.",
                ],
                lines=[],
                choices=[],
                ending="The Rain Does Not Ask",
            ),
            "ending-warm": _st(
                id="ending-warm",
                chapter=3,
                title="Second Chances, Warm",
                narration=[
                    "Honesty lands on the table between you like a shared umbrella. Alex exhales, smiles with their whole face this time, and says the words you didn't know you were waiting for:",
                    "“Then let's stop hoping at a distance.” They lift their cup. “To rain, again.” Outside, the storm finally begins to lose its argument with the streetlights — but neither of you notices.",
                ],
                lines=[],
                choices=[],
                ending="Second Chances, Warm",
            ),
        },
    },
}
