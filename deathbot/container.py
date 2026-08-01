"""Composition root — builds and wires every layer once at startup.

The container is stashed on the aiogram Dispatcher's workflow data, so any
handler can pull the services it needs without global state.
"""
from __future__ import annotations

from dataclasses import dataclass

from .agents import Agent, build_agents
from .ai import AIRouter
from .config import Settings
from .core.security import Crypto
from .db import Database
from .repositories import Repositories
from .tasks import BackgroundTasks
from .tools import TaskEngine
from .services import (
    AccessControlService,
    AIService,
    ApiKeyService,
    ExportService,
    NotesService,
    NotificationService,
    OSINTService,
    PentestService,
    PluginService,
    ReportService,
    SettingsService,
    TodoService,
    UserService,
)


@dataclass
class Container:
    settings: Settings
    db: Database
    repos: Repositories
    crypto: Crypto
    ai_router: AIRouter

    access: AccessControlService
    users: UserService
    notes: NotesService
    todos: TodoService
    api_keys: ApiKeyService
    settings_svc: SettingsService
    ai: AIService
    osint: OSINTService
    pentest: PentestService
    plugins: PluginService
    report: ReportService
    export: ExportService
    engine: TaskEngine
    background: BackgroundTasks
    agents: dict[str, Agent]
    notifications: NotificationService | None = None

    @classmethod
    def build(cls, settings: Settings) -> "Container":
        db = Database(settings.absolute_db_path())
        repos = Repositories.build(db)
        crypto = Crypto.from_settings(settings.secret_key, settings.absolute_key_path())
        ai_router = AIRouter(settings)
        api_keys = ApiKeyService(repos, crypto)

        return cls(
            settings=settings,
            db=db,
            repos=repos,
            crypto=crypto,
            ai_router=ai_router,
            access=AccessControlService(settings, repos),
            users=UserService(repos),
            notes=NotesService(repos),
            todos=TodoService(repos),
            api_keys=api_keys,
            settings_svc=SettingsService(repos),
            ai=AIService(settings, repos, ai_router, api_keys),
            osint=OSINTService(settings, repos, api_keys),
            pentest=PentestService(repos),
            plugins=PluginService(repos),
            report=ReportService(),
            export=ExportService(),
            engine=TaskEngine(workers=4),
            background=BackgroundTasks(repos),
            agents=build_agents(ai_router),
        )

    async def startup(self) -> None:
        await self.db.init_schema()
        await self.engine.start()
        await self.background.start()
        await self.plugins.bootstrap()

    async def shutdown(self) -> None:
        await self.background.stop()
        await self.engine.stop()
        await self.db.close()
