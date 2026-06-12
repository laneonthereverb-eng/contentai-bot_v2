from bot.handlers.commands import router as commands_router
from bot.handlers.content import router as content_router
from bot.handlers.payments import router as payments_router

__all__ = ["commands_router", "content_router", "payments_router"]