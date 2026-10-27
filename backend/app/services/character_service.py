"""Character service: all character-related business logic.

Routes never touch the data modules directly — they ask a service, so
the data source can change (files → PostgreSQL) without touching the API.
"""

from fastapi import HTTPException

from app.data.characters import CHARACTERS
from app.schemas import CharacterListOut


def list_characters() -> CharacterListOut:
    return CharacterListOut.model_validate(
        {"characters": CHARACTERS}
    )


def get_character_or_404(character_id: str) -> dict:
    for character in CHARACTERS:
        if character["id"] == character_id:
            return dict(character)
    raise HTTPException(
        status_code=404,
        detail=f"Character '{character_id}' not found.",
    )
