"""Authentication: password hashing + token issuing/verification.

Approach (all well-maintained libraries):
  - bcrypt  — industry-standard password hashing (salted, slow by design)
  - PyJWT   — signs login tokens; the signature proves a token is ours

Security rules enforced here:
  - passwords are NEVER stored in plaintext
  - a request proves identity ONLY by presenting a valid token —
    user ids sent in request bodies are never trusted
"""

from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User

ALGORITHM = "HS256"

# Swagger UI shows a "Authorize" button; requests carry:
#   Authorization: Bearer <token>
_bearer = HTTPBearer(auto_error=False)


def hash_password(plain: str) -> str:
    hashed = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS))
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_token(user_id: str) -> str:
    payload = {
        "sub": user_id,  # "subject": whose token this is
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(days=settings.TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def _decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return str(payload["sub"])
    except jwt.ExpiredSignatureError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session has expired. Please log in again.",
        ) from err
    except jwt.InvalidTokenError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing login token.",
        ) from err


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency: resolves the User from the Bearer token.

    Every private endpoint depends on this — identity comes ONLY from
    the signed token, never from anything the client claims in a body.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = _decode_token(credentials.credentials)
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account no longer exists.",
        )
    return user
