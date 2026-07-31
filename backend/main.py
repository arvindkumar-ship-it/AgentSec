# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from contextlib import asynccontextmanager
# from core.db import connect_db, close_db
# from routes import scan_routes, shield_routes, eval_routes, dashboard_routes, auth_routes


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await connect_db()
#     yield
#     await close_db()


# app = FastAPI(
#     title="AgentSec — AI Agent Security Platform",
#     description="3-layer security for your AI agents: Scan + Shield + Eval",
#     version="1.0.0",
#     lifespan=lifespan,
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000", "https://agent-sec-teal.vercel.app"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(auth_routes.router)
# app.include_router(scan_routes.router)
# app.include_router(shield_routes.router)
# app.include_router(eval_routes.router)
# app.include_router(dashboard_routes.router)


# @app.get("/")
# async def root():
#     return {
#         "service": "AgentSec",
#         "status": "running",
#         "layers": ["Agent Scan", "Agent Shield", "Agent Eval"],
#         "docs": "/docs"
#     }


# @app.get("/health")
# async def health():
#     return {"status": "healthy"}

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from contextlib import asynccontextmanager
# from core.db import connect_db, close_db
# from routes import scan_routes, shield_routes, eval_routes, dashboard_routes, auth_routes, agent_config_routes
# from routes.reports import router as reports_router
# from routes.auth_routes import router as auth_router
# async def lifespan(app: FastAPI):
#     await connect_db()
#     yield
#     await close_db()


# app = FastAPI(
#     title="AgentSec — AI Agent Security Platform",
#     description="3-layer security for your AI agents: Scan + Shield + Eval",
#     version="1.0.0",
#     lifespan=lifespan,
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000", "https://agent-sec-teal.vercel.app"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(auth_routes.router)
# app.include_router(scan_routes.router)
# app.include_router(scan_routes.agentsec_scan_router)
# app.include_router(shield_routes.router)
# app.include_router(eval_routes.router)
# app.include_router(eval_routes.agentsec_eval_router)
# app.include_router(dashboard_routes.router)
# app.include_router(agent_config_routes.router)
# app.include_router(reports_router)
# app.include_router(auth_router)
# @asynccontextmanager

# @app.get("/")
# async def root():
#     return {
#         "service": "AgentSec",
#         "status": "running",
#         "layers": ["Agent Scan", "Agent Shield", "Agent Eval"],
#         "docs": "/docs"
#     }


# @app.get("/health")
# async def health():
#     return {"status": "healthy"}






import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
import sentry_sdk

from config import settings
from core.db import connect_db, close_db, get_db
from core.limiter import limiter
from core.logging_config import setup_logging
from core.request_context import RequestContextMiddleware
from database import engine
from routes import scan_routes, shield_routes, eval_routes, dashboard_routes, auth_routes, agent_config_routes, admin_routes, policy_routes, audit_routes, billing_routes
from routes.reports import router as reports_router


if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=0.2,
        environment="production",
        send_default_pii=False,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    from database import SessionLocal
    from services.quota_service import seed_plans
    async with SessionLocal() as session:
        await seed_plans(session)
    yield
    await close_db()


IS_PRODUCTION = os.getenv("ENVIRONMENT", "development") == "production"

app = FastAPI(
    title="AgentSec — AI Agent Security Platform",
    description="3-layer security for your AI agents: Scan + Shield + Eval",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
)

setup_logging()
app.add_middleware(RequestContextMiddleware)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://agent-sec-teal.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(scan_routes.router)
app.include_router(scan_routes.agentsec_scan_router)
app.include_router(shield_routes.router)
app.include_router(eval_routes.router)
app.include_router(eval_routes.agentsec_eval_router)
app.include_router(dashboard_routes.router)
app.include_router(agent_config_routes.router)
app.include_router(reports_router)
app.include_router(admin_routes.router)
app.include_router(policy_routes.router)
app.include_router(audit_routes.router)
app.include_router(billing_routes.router)


@app.get("/")
async def root():
    return {
        "service": "AgentSec",
        "status": "running",
        "layers": ["Agent Scan", "Agent Shield", "Agent Eval"],
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    checks = {"postgres": "unknown", "mongodb": "unknown"}
    healthy = True

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["postgres"] = "ok"
    except Exception as e:
        checks["postgres"] = f"error: {str(e)[:100]}"
        healthy = False

    try:
        db = get_db()
        if db is None:
            raise Exception("MongoDB not connected")
        await db.command("ping")
        checks["mongodb"] = "ok"
    except Exception as e:
        checks["mongodb"] = f"error: {str(e)[:100]}"
        healthy = False

    status_code = 200 if healthy else 503
    return JSONResponse(
        status_code=status_code,
        content={"status": "healthy" if healthy else "unhealthy", "checks": checks},
    )