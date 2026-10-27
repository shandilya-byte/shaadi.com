"""EverAfter FastAPI application entrypoint (Phase 5).

Run from the backend/ folder with:
    .venv\Scripts\Activate.ps1
    uvicorn app.main:app --reload --port 8000

Interactive API docs (Swagger UI): http://localhost:8000/docs

Auth model:
  - POST /api/auth/register and /api/auth/login are public.
  - Everything under /api/my/* is private: identity comes ONLY from
    the Bearer token (never from a user id in the request body), and
    each user can only ever see and change their own progress.
"""

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import auth
from app.database import Base, engine, get_db
from app.models import User
from app.schemas import (
    CharacterListOut,
    ChoiceRequest,
    LoginRequest,
    ProgressOut,
    RegisterRequest,
    StoryInfoOut,
    TokenOut,
    UserOut,
)
from app.services import character_service, story_service

app = FastAPI(
    title="EverAfter API",
    description="Backend for the EverAfter interactive romance experience.",
    version="0.5.0",
)

# ── CORS ─────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.on_event("startup")
def create_tables() -> None:
    """Dev convenience: create any missing tables on startup.

    For real migrations (column changes, renames) use Alembic — see
    README section in the phase notes. create_all never drops data.
    """
    Base.metadata.create_all(engine)


# ── Health & public content ──────────────────────────────────────────
@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/characters", response_model=CharacterListOut)
def list_characters() -> CharacterListOut:
    return character_service.list_characters()


@app.get("/api/stories/{story_id}", response_model=StoryInfoOut)
def get_story(story_id: str) -> StoryInfoOut:
    """Story metadata + the opening scene (public — browsing is free)."""
    return story_service.get_story_info(story_id)


# ── Auth ─────────────────────────────────────────────────────────────
@app.post("/api/auth/register", response_model=TokenOut, status_code=201)
def register(request: RegisterRequest, db: Session = Depends(get_db)) -> TokenOut:
    existing = db.scalars(
        select(User).where(User.email == request.email.lower())
    ).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail="That email is already registered.")

    user = User(
        email=request.email.lower(),
        display_name=request.display_name.strip(),
        hashed_password=auth.hash_password(request.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenOut(access_token=auth.create_token(user.id), user=UserOut.model_validate(user))


@app.post("/api/auth/login", response_model=TokenOut)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> TokenOut:
    from fastapi import HTTPException

    user = db.scalars(
        select(User).where(User.email == request.email.lower())
    ).first()
    # Same message for wrong email and wrong password — don't leak
    # which emails exist.
    if user is None or not auth.verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    return TokenOut(access_token=auth.create_token(user.id), user=UserOut.model_validate(user))


@app.get("/api/auth/me", response_model=UserOut)
def me(user: User = Depends(auth.get_current_user)) -> UserOut:
    return UserOut.model_validate(user)


# ── Private story endpoints (token required, per-user data) ──────────
@app.post("/api/my/stories/{story_id}/start", response_model=ProgressOut)
def start_story(
    story_id: str,
    user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
) -> ProgressOut:
    """Start (or resume) the user's playthrough of a story."""
    return story_service.start_story(db, user, story_id)


@app.get("/api/my/stories/{story_id}/progress", response_model=ProgressOut)
def get_progress(
    story_id: str,
    user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
) -> ProgressOut:
    """The user's saved scene + relationship variables."""
    return story_service.get_progress(db, user, story_id)


@app.post("/api/my/stories/{story_id}/choice", response_model=ProgressOut)
def submit_choice(
    story_id: str,
    request: ChoiceRequest,
    user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
) -> ProgressOut:
    """Validate the choice, apply effects, advance — and log the event."""
    return story_service.apply_choice(db, user, story_id, request.choice_id)


@app.post("/api/my/stories/{story_id}/restart", response_model=ProgressOut)
def restart_story(
    story_id: str,
    user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
) -> ProgressOut:
    return story_service.restart_story(db, user, story_id)


@app.get("/api/my/stories/{story_id}/events")
def list_events(
    story_id: str,
    user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    """The user's own chosen-dialogue history (Phase 7 scrapbook input)."""
    events = story_service.list_events(db, user, story_id)
    return [
        {
            "node_id": e.node_id,
            "choice_id": e.choice_id,
            "chapter": e.chapter,
            "vars_after": e.vars_after,
            "created_at": e.created_at.isoformat(),
        }
        for e in events
    ]
