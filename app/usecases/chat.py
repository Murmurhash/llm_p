from app.db.models import ChatMessage
from app.repositories.chat_messages import ChatMessagesRepository
from app.services.openrouter_client import OpenRouterClient


class ChatUseCase:
    """Business logic for chatting with the LLM.

    Responsibilities:
      * build the list of messages sent to the model (system + history + new prompt),
      * persist the user's prompt and the model's answer to the DB,
      * return the model's text answer to the caller.

    This class never creates DB sessions directly: it only talks to a repository
    and a service.
    """

    def __init__(
        self,
        messages_repo: ChatMessagesRepository,
        openrouter: OpenRouterClient,
    ) -> None:
        self._messages_repo = messages_repo
        self._openrouter = openrouter

    async def ask(
        self,
        user_id: int,
        prompt: str,
        system: str | None = None,
        max_history: int = 10,
        temperature: float = 0.7,
    ) -> str:
        # 1. Build message list for the LLM.
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})

        history = await self._messages_repo.list_last_for_user(
            user_id=user_id, limit=max_history
        )
        for m in history:
            messages.append({"role": m.role, "content": m.content})

        messages.append({"role": "user", "content": prompt})

        # 2. Persist the user's prompt before calling the model, so it is saved
        #    even if the external call fails.
        await self._messages_repo.add(user_id=user_id, role="user", content=prompt)

        # 3. Call the LLM.
        answer = await self._openrouter.chat_completion(
            messages=messages, temperature=temperature
        )

        # 4. Persist the assistant's answer.
        await self._messages_repo.add(
            user_id=user_id, role="assistant", content=answer
        )

        return answer

    async def get_history(self, user_id: int) -> list[ChatMessage]:
        return await self._messages_repo.list_all_for_user(user_id)

    async def clear_history(self, user_id: int) -> int:
        return await self._messages_repo.delete_all_for_user(user_id)
