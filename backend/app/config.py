"""App configuration, loaded from environment variables.

The backend/.env file holds real values for local development and is
NEVER committed to git. backend/.env.example shows the required keys
with placeholder values instead of real secrets.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load backend/.env (file lives one level above this package).
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def _required(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable '{key}'. "
            "Copy backend/.env.example to backend/.env and fill it in."
        )
    return value


class Settings:
    # SQLAlchemy connection string, e.g.
    # postgresql+psycopg://everafter:PASSWORD@localhost:5433/everafter
    DATABASE_URL: str = _required("DATABASE_URL")

    # Secret used to sign login tokens. Generate one with:
    #   python -c "import secrets; print(secrets.token_hex(32))"
    SECRET_KEY: str = _required("SECRET_KEY")

    # Days until a login token expires.
    TOKEN_EXPIRE_DAYS: int = int(os.getenv("TOKEN_EXPIRE_DAYS", "7"))

    # bcrypt hashing cost (higher = slower + stronger; 12 is standard).
    BCRYPT_ROUNDS: int = int(os.getenv("BCRYPT_ROUNDS", "12"))


settings = Settings()
