"""Story service: the story engine, now database-backed.

Identity note: every function receives the authenticated User object
resolved from their login token by FastAPI — never a user id sent by
the client. Ownership is enforced by looking up progress rows by
(user.id, story_id), so a user can only ever touch their own progress.
"""

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.stories import STARTING_VARS, STORIES
from app.models import StoryEvent, StoryProgress, User
from app.schemas import NodeOut, ProgressOut, StoryInfoOut


def get_story_or_404(story_id: str) -> dict:
    story = STORIES.get(story_id)
    if story is None:
        raise HTTPException(
            status_code=404, detail=f"Story '{story_id}' not found."
        )
    return dict(story)


def get_story_info(story_id: str) -> StoryInfoOut:
    story = get_story_or_404(story_id)
    return StoryInfoOut.model_validate(
        {
            **{
                k: story[k]
                for k in (
                    "id", "title", "character_name",
                    "character_initial", "gradient", "total_chapters",
                )
            },
            "opening_node": _node_out(story, story["start_node"]),
        }
    )


def start_story(db: Session, user: User, story_id: str) -> ProgressOut:
    """Return the user's playthrough — resuming an existing one if the
    user has already started this story (so "start" never wipes data)."""
    story = get_story_or_404(story_id)
    progress = _get_or_create_progress(db, user, story)
    return _progress_out(story, progress)


def get_progress(db: Session, user: User, story_id: str) -> ProgressOut:
    story = get_story_or_404(story_id)
    progress = _get_progress_or_404(db, user, story_id)
    return _progress_out(story, progress)


def apply_choice(
    db: Session, user: User, story_id: str, choice_id: str
) -> ProgressOut:
    story = get_story_or_404(story_id)
    progress = _get_progress_or_404(db, user, story_id)
    node = story["nodes"][progress.node_id]

    if node["ending"] is not None:
        raise HTTPException(
            status_code=400,
            detail="This story has already ended. Restart to play again.",
        )

    # Core validation: the choice must belong to THIS scene.
    choice = next(
        (c for c in node["choices"] if c["id"] == choice_id), None
    )
    if choice is None:
        raise HTTPException(
            status_code=400,
            detail=f"Choice '{choice_id}' does not belong to scene '{progress.node_id}'.",
        )

    # And its target node must actually exist.
    next_node = story["nodes"].get(choice["next"])
    if next_node is None:
        raise HTTPException(
            status_code=500,
            detail=f"Story data error: choice '{choice_id}' leads to missing node '{choice['next']}'.",
        )

    new_vars = {
        key: progress.vars.get(key, 0) + choice["effects"].get(key, 0)
        for key in ("trust", "playfulness", "openness")
    }
    progress.node_id = choice["next"]
    progress.vars = new_vars
    progress.finished = next_node["ending"] is not None

    # Log the event (chosen dialogue) — future scrapbook material.
    db.add(
        StoryEvent(
            progress_id=progress.id,
            user_id=user.id,
            story_id=story_id,
            node_id=node["id"],
            choice_id=choice_id,
            chapter=node["chapter"],
            vars_after=new_vars,
        )
    )
    db.commit()
    db.refresh(progress)
    return _progress_out(story, progress)


def restart_story(db: Session, user: User, story_id: str) -> ProgressOut:
    story = get_story_or_404(story_id)
    progress = _get_progress_or_404(db, user, story_id)
    progress.node_id = story["start_node"]
    progress.vars = dict(STARTING_VARS)
    progress.finished = False
    db.commit()
    db.refresh(progress)
    return _progress_out(story, progress)


def list_events(db: Session, user: User, story_id: str) -> list[StoryEvent]:
    """The user's own choice history (future scrapbook input)."""
    return list(
        db.scalars(
            select(StoryEvent)
            .where(StoryEvent.user_id == user.id, StoryEvent.story_id == story_id)
            .order_by(StoryEvent.created_at)
        )
    )


# ── internal helpers ─────────────────────────────────────────────────

def _get_progress_or_404(
    db: Session, user: User, story_id: str
) -> StoryProgress:
    progress = db.scalars(
        select(StoryProgress).where(
            StoryProgress.user_id == user.id,
            StoryProgress.story_id == story_id,
        )
    ).first()
    if progress is None:
        raise HTTPException(
            status_code=404,
            detail=f"You have no '{story_id}' playthrough yet. Start the story first.",
        )
    return progress


def _get_or_create_progress(
    db: Session, user: User, story: dict
) -> StoryProgress:
    progress = db.scalars(
        select(StoryProgress).where(
            StoryProgress.user_id == user.id,
            StoryProgress.story_id == story["id"],
        )
    ).first()
    if progress is None:
        progress = StoryProgress(
            user_id=user.id,
            story_id=story["id"],
            node_id=story["start_node"],
            vars=dict(STARTING_VARS),
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
    return progress


def _node_out(story: dict, node_id: str) -> NodeOut:
    return NodeOut.model_validate(story["nodes"][node_id])


def _progress_out(story: dict, progress: StoryProgress) -> ProgressOut:
    node = story["nodes"][progress.node_id]
    return ProgressOut.model_validate(
        {
            "progress_id": progress.id,
            "story_id": progress.story_id,
            "finished": progress.finished,
            "chapter": node["chapter"],
            "total_chapters": story["total_chapters"],
            "vars": progress.vars,
            "node": _node_out(story, progress.node_id),
        }
    )
