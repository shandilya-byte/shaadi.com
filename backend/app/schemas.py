"""Pydantic schemas: the shapes of our API requests and responses.

Pydantic checks every incoming request automatically — if a field is
missing or the wrong type, FastAPI rejects it with a clear 422 error
before any of our code runs.
"""

from pydantic import BaseModel, EmailStr, Field

# ── Auth requests/responses ──────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    display_name: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    id: str
    email: str
    display_name: str

    # Allow building this schema straight from an ORM User object.
    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ── Responses ────────────────────────────────────────────────────────
class CharacterOut(BaseModel):
    id: str
    name: str
    title: str
    tagline: str
    genre: str
    traits: list[str]
    moods: list[str]
    initial: str
    gradient: str


class CharacterListOut(BaseModel):
    characters: list[CharacterOut]


class ChoiceOut(BaseModel):
    id: str
    label: str


class StoryLineOut(BaseModel):
    speaker: str
    text: str


class NodeOut(BaseModel):
    """One story scene, as the player should see it."""

    id: str
    chapter: int
    title: str
    narration: list[str]
    lines: list[StoryLineOut]
    choices: list[ChoiceOut]
    ending: str | None = None


class StoryVarsOut(BaseModel):
    trust: int
    playfulness: int
    openness: int


class StoryInfoOut(BaseModel):
    """Story metadata + the opening scene (for the story page)."""

    id: str
    title: str
    character_name: str
    character_initial: str
    gradient: str
    total_chapters: int
    opening_node: NodeOut


class ProgressOut(BaseModel):
    """The full playable state after starting / loading / choosing."""

    progress_id: str
    story_id: str
    finished: bool
    chapter: int
    total_chapters: int
    vars: StoryVarsOut
    node: NodeOut


# ── Requests ─────────────────────────────────────────────────────────
class ChoiceRequest(BaseModel):
    choice_id: str = Field(min_length=1, max_length=64)


class RestartRequest(BaseModel):
    pass  # the user comes from the token; no body needed
