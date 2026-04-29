from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import AsyncSessionLocal
from app.repositories.chat_messages import ChatMessagesRepository
from app.repositories.users import UsersRepository
from app.services.openrouter_client import OpenRouterClient
from app.usecases.auth import AuthUseCase
from app.usecases.chat import ChatUseCase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a SQLAlchemy AsyncSession per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# --- Repositories ------------------------------------------------------------

def get_users_repo(
    session: AsyncSession = Depends(get_session),
) -> UsersRepository:
    return UsersRepository(session)


def get_chat_messages_repo(
    session: AsyncSession = Depends(get_session),
) -> ChatMessagesRepository:
    return ChatMessagesRepository(session)


# --- Services ----------------------------------------------------------------

def get_openrouter_client() -> OpenRouterClient:
    return OpenRouterClient()


# --- Usecases ----------------------------------------------------------------

def get_auth_usecase(
    users_repo: UsersRepository = Depends(get_users_repo),
) -> AuthUseCase:
    return AuthUseCase(users_repo)


def get_chat_usecase(
    messages_repo: ChatMessagesRepository = Depends(get_chat_messages_repo),
    openrouter: OpenRouterClient = Depends(get_openrouter_client),
) -> ChatUseCase:
    return ChatUseCase(messages_repo=messages_repo, openrouter=openrouter)


# --- Current user ------------------------------------------------------------

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """Decode the Bearer JWT and return the current user's id.

    Raises HTTP 401 on any problem. This is an infrastructure-layer concern,
    so mapping domain issues to HTTP here is acceptable.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
    except JWTError as exc:
        raise credentials_exception from exc

    sub = payload.get("sub")
    if sub is None:
        raise credentials_exception
    try:
        return int(sub)
    except (TypeError, ValueError) as exc:
        raise credentials_exception from exc
