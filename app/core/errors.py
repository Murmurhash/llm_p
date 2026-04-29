"""Domain-level exceptions used by usecases and services.

Usecase / service code must raise these (not FastAPI's HTTPException).
The API layer is responsible for mapping them to HTTP responses.
"""


class AppError(Exception):
    """Base class for all application-level errors."""

    def __init__(self, message: str = "Application error") -> None:
        super().__init__(message)
        self.message = message


class ConflictError(AppError):
    """Raised when a resource already exists (e.g. email already registered)."""

    def __init__(self, message: str = "Resource already exists") -> None:
        super().__init__(message)


class UnauthorizedError(AppError):
    """Raised when credentials are missing or invalid."""

    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message)


class ForbiddenError(AppError):
    """Raised when the authenticated user is not allowed to perform an action."""

    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(message)


class NotFoundError(AppError):
    """Raised when a requested entity does not exist."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message)


class ExternalServiceError(AppError):
    """Raised when a call to an external service (e.g. OpenRouter) fails."""

    def __init__(
        self,
        message: str = "External service error",
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
