from typing import Any

import httpx

from app.core.config import settings
from app.core.errors import ExternalServiceError


class OpenRouterClient:
    """Thin async client for the OpenRouter /chat/completions endpoint.

    Does not know about users, JWT, or the database. All persistence decisions
    are made by the chat usecase; this class only speaks HTTP to OpenRouter.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        site_url: str | None = None,
        app_name: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        self._api_key = api_key if api_key is not None else settings.openrouter_api_key
        self._base_url = (base_url or settings.openrouter_base_url).rstrip("/")
        self._model = model or settings.openrouter_model
        self._site_url = site_url or settings.openrouter_site_url
        self._app_name = app_name or settings.openrouter_app_name
        self._timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self._site_url,
            "X-Title": self._app_name,
        }

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        model: str | None = None,
    ) -> str:
        """Send a chat-completion request and return the assistant's text answer.

        Raises ExternalServiceError on any non-2xx response or transport failure.
        """
        if not self._api_key:
            raise ExternalServiceError(
                "OPENROUTER_API_KEY is not configured", status_code=500
            )

        url = f"{self._base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": model or self._model,
            "messages": messages,
            "temperature": temperature,
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(url, headers=self._headers(), json=payload)
        except httpx.HTTPError as exc:
            raise ExternalServiceError(
                f"Failed to reach OpenRouter: {exc!s}"
            ) from exc

        if response.status_code >= 400:
            raise ExternalServiceError(
                f"OpenRouter returned {response.status_code}: {response.text}",
                status_code=response.status_code,
            )

        try:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError) as exc:
            raise ExternalServiceError(
                f"Unexpected OpenRouter response shape: {exc!s}"
            ) from exc
