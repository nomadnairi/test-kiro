"""Bot & Dispatcher assembly and the polling entrypoint."""
from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from .config import Settings, load_settings
from .container import Container
from .handlers import build_root_router
from .logging_setup import get_logger, setup_logging
from .middlewares import (
    AuthMiddleware,
    LoggingMiddleware,
    MaintenanceMiddleware,
    RateLimitMiddleware,
)
from .services import NotificationService

log = get_logger("bot")


def build_dispatcher(container: Container) -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())

    # Make the container injectable everywhere (handlers, filters, middlewares).
    dp["container"] = container

    # Order matters: logging → maintenance → auth → rate-limit → handler.
    for event in (dp.message, dp.callback_query):
        event.middleware(LoggingMiddleware())
        event.middleware(MaintenanceMiddleware())
        event.middleware(AuthMiddleware())
        event.middleware(RateLimitMiddleware())

    dp.include_router(build_root_router())
    return dp


def create_bot(settings: Settings) -> Bot:
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=settings.parse_mode),
    )


async def run(settings: Settings | None = None) -> None:
    settings = settings or load_settings()
    setup_logging(settings.log_level)

    if not settings.bot_token or settings.bot_token.startswith("123456:REPLACE"):
        raise SystemExit("BOT_TOKEN is not set — copy .env.example to .env and fill it in.")

    container = Container.build(settings)
    await container.startup()

    bot = create_bot(settings)
    container.notifications = NotificationService(bot, settings.owner_id)
    dp = build_dispatcher(container)

    log.info("DeathBot starting (env=%s, providers=%s)",
             settings.env, ", ".join(container.ai.available_providers()) or "none")
    try:
        await dp.start_polling(bot)
    finally:
        await container.shutdown()
        await bot.session.close()
