from app.core.errors import ConflictError, NotFoundError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import User
from app.repositories.users import UsersRepository


class AuthUseCase:
    """Business logic for registration, login, and profile lookup.

    Pure domain logic: no FastAPI, no HTTPException, no SQL.
    Raises domain exceptions from `app.core.errors`.
    """

    def __init__(self, users_repo: UsersRepository) -> None:
        self._users_repo = users_repo

    async def register(self, email: str, password: str) -> User:
        existing = await self._users_repo.get_by_email(email)
        if existing is not None:
            raise ConflictError("User with this email already exists")

        password_hash_value = hash_password(password)
        return await self._users_repo.create(
            email=email,
            password_hash=password_hash_value,
            role="user",
        )

    async def login(self, email: str, password: str) -> str:
        user = await self._users_repo.get_by_email(email)
        if user is None:
            raise UnauthorizedError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")

        return create_access_token(subject=user.id, role=user.role)

    async def get_profile(self, user_id: int) -> User:
        user = await self._users_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")
        return user
