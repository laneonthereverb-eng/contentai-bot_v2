from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
import time
from collections import defaultdict

class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limit: int = 5, period: int = 60):
        self.limit = limit
        self.period = period
        self.user_timestamps: Dict[int, list] = defaultdict(list)
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        now = time.time()
        
        self.user_timestamps[user_id] = [
            ts for ts in self.user_timestamps[user_id]
            if now - ts < self.period
        ]
        
        if len(self.user_timestamps[user_id]) >= self.limit:
            if isinstance(event, Message):
                await event.answer("Слишком много запросов. Подождите немного.")
            elif isinstance(event, CallbackQuery):
                await event.answer("Слишком много запросов", show_alert=True)
            return None
        
        self.user_timestamps[user_id].append(now)
        return await handler(event, data)