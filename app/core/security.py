from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    return _pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Check a plain-text password against a bcrypt hash."""
    return _pwd_context.verify(plain_password, password_hash)


def create_access_token(
    subject: str | int,
    role: str = "user",
    expires_minutes: int | None = None,
) -> str:
    """Create a signed JWT access token containing sub/role/iat/exp claims."""
    now = datetime.now(tz=UTC)
    expire_delta = timedelta(
        minutes=expires_minutes
        if expires_minutes is not None
        else settings.access_token_expire_minutes
    )
    payload: dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + expire_delta).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token. Returns the payload dict.

    Raises jose.JWTError (or subclass) on invalid signature / expired token.
    """
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
    except JWTError:
        raise
