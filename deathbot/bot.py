"""Bot & Dispatcher assembly and the polling entrypoint."""
from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from .ai import AIRouter
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


async def doctor(settings: Settings | None = None) -> int:
    """`python -m deathbot --check` — explain why the bot might not be answering."""
    settings = settings or load_settings()
    setup_logging("WARNING")
    problems = 0

    def line(ok: bool, text: str) -> None:
        nonlocal problems
        print(f"  [{'OK ' if ok else 'FAIL'}] {text}")
        if not ok:
            problems += 1

    print("DeathBot self-check\n")

    token = settings.bot_token
    has_token = bool(token) and not token.startswith("123456:REPLACE")
    line(has_token, f"BOT_TOKEN: {token[:8] + '…' if has_token else 'NOT SET (.env)'}")
    line(bool(settings.owner_id),
         f"OWNER_ID: {settings.owner_id or 'NOT SET — you will be a guest with an almost empty menu'}")

    db = settings.absolute_db_path()
    try:
        db.parent.mkdir(parents=True, exist_ok=True)
        line(True, f"database path writable: {db}")
    except OSError as exc:
        line(False, f"database path NOT writable: {db} ({exc})")

    if not has_token:
        print("\nFix BOT_TOKEN first, then run this again.")
        return 1

    bot = create_bot(settings)
    try:
        me = await bot.get_me()
        line(True, f"Telegram reachable, bot is @{me.username} (id={me.id})")

        info = await bot.get_webhook_info()
        if info.url:
            line(False, f"a webhook is set ({info.url}) — long polling cannot work, "
                        "start the bot normally and it will be removed")
        else:
            line(True, "no webhook set (long polling can run)")
        if info.pending_update_count:
            print(f"  [i]   {info.pending_update_count} pending updates queued")
    except TelegramAPIError as exc:
        line(False, f"Telegram rejected the token: {exc}")
    finally:
        await bot.session.close()

    providers = AIRouter(settings).available_providers()
    print(f"  [i]   AI providers configured: {', '.join(providers) or 'none'}")

    print("\n" + ("All good — if the bot still ignores you, make sure only ONE instance "
                  "is running with this token." if problems == 0
                  else f"{problems} problem(s) found — fix the FAIL lines above."))
    return 0 if problems == 0 else 1


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

    # Fail loudly and early if the token is wrong — otherwise the bot just sits
    # there silently and looks "dead" in the chat.
    try:
        me = await bot.get_me()
    except TelegramAPIError as exc:
        await container.shutdown()
        await bot.session.close()
        raise SystemExit(f"Telegram rejected BOT_TOKEN: {exc}") from exc
    log.info("Connected to Telegram as @%s (id=%s)", me.username, me.id)

    if not settings.owner_id:
        log.warning(
            "OWNER_ID is not set — you will be treated as a guest and see an "
            "almost empty menu. Put your Telegram user id in OWNER_ID."
        )

    # A webhook left on this token makes long-polling fail with 409 Conflict and
    # the bot answers nothing at all. Clear it before polling.
    await bot.delete_webhook(drop_pending_updates=True)

    # Show /start, /menu, /cancel in Telegram's command menu.
    await bot.set_my_commands([
        BotCommand(command="start", description="Открыть меню"),
        BotCommand(command="menu", description="Открыть меню"),
        BotCommand(command="cancel", description="Отменить текущее действие"),
    ])

    log.info("DeathBot started (env=%s, owner=%s, AI providers=%s)",
             settings.env, settings.owner_id or "UNSET",
             ", ".join(container.ai_router.available_providers()) or "none")
    try:
        await dp.start_polling(bot)
    finally:
        await container.shutdown()
        await bot.session.close()
