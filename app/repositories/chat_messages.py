from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ChatMessage


class ChatMessagesRepository:
    """Data-access layer for the `chat_messages` table.

    Only handles SQL/ORM. Does not know about OpenRouter or context-building rules.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, user_id: int, role: str, content: str) -> ChatMessage:
        message = ChatMessage(user_id=user_id, role=role, content=content)
        self._session.add(message)
        await self._session.commit()
        await self._session.refresh(message)
        return message

    async def list_last_for_user(self, user_id: int, limit: int) -> list[ChatMessage]:
        """Return the last `limit` messages for the user, ordered chronologically (oldest first)."""
        if limit <= 0:
            return []
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.id.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        messages = list(result.scalars().all())
        messages.reverse()
        return messages

    async def list_all_for_user(self, user_id: int) -> list[ChatMessage]:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.id.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def delete_all_for_user(self, user_id: int) -> int:
        stmt = delete(ChatMessage).where(ChatMessage.user_id == user_id)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount or 0
