"""Analytics service API.  Run: ``uvicorn analytics_service.main:app --port 8002``"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Query, Request
from sqlalchemy import func, select, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from service_common import configure_logging, create_app, dependency

from . import __version__
from .config import Settings
from .db import Base, Interaction, make_engine, make_session_factory
from .schemas import InteractionIn, InteractionOut, InteractionPage, Stats
from .stats import baku_today, compute_stats, period_start

SERVICE = "analytics"


def _session(request: Request):
    with request.app.state.sessions() as db, dependency("database", OperationalError):  # connection lost / refused
        yield db


Db = Annotated[Session, Depends(_session)]


def build_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    configure_logging(SERVICE, settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine = make_engine(settings.database_url)
        with dependency("database", OperationalError):
            await run_in_threadpool(Base.metadata.create_all, engine)
        app.state.engine, app.state.sessions = engine, make_session_factory(engine)
        yield
        engine.dispose()

    app = create_app(SERVICE, __version__, ready_checks=_ready_checks, lifespan=lifespan)

    @app.post("/v1/interactions", response_model=InteractionOut, status_code=201, tags=["interactions"])
    def record(body: InteractionIn, db: Db) -> Interaction:
        row = Interaction(**body.model_dump())
        db.add(row)
        db.commit()
        return row

    @app.get("/v1/interactions", response_model=InteractionPage, tags=["interactions"])
    def browse(db: Db, limit: Annotated[int, Query(ge=1, le=200)] = 50, offset: Annotated[int, Query(ge=0)] = 0,
               status: str | None = None) -> InteractionPage:
        query = select(Interaction)
        if status:
            query = query.where(Interaction.status == status)
        total = db.scalar(select(func.count()).select_from(query.subquery()))
        rows = db.scalars(query.order_by(Interaction.created_at.desc(), Interaction.id.desc())
                          .limit(limit).offset(offset)).all()
        return InteractionPage(items=[InteractionOut.model_validate(row) for row in rows], total=total)

    @app.get("/v1/stats", response_model=Stats, tags=["interactions"])
    def stats(db: Db, days: Annotated[int, Query(ge=1, le=365)] = 30) -> Stats:
        today = baku_today()
        rows = db.scalars(select(Interaction).where(Interaction.created_at >= period_start(days, today))).all()
        return compute_stats(rows, days, today)

    return app


def _ready_checks(app: FastAPI):
    async def database() -> str:
        def count() -> int:
            with app.state.sessions() as db:
                db.execute(text("SELECT 1"))
                return db.scalar(select(func.count()).select_from(Interaction))
        return f"{await run_in_threadpool(count)} interactions stored"

    return {"database": database}


app = build_app()
