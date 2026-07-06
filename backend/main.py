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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.db import connect_db, close_db
from routes import scan_routes, shield_routes, eval_routes, dashboard_routes, auth_routes, agent_config_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="AgentSec — AI Agent Security Platform",
    description="3-layer security for your AI agents: Scan + Shield + Eval",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://agent-sec-teal.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(scan_routes.router)
app.include_router(shield_routes.router)
app.include_router(eval_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(agent_config_routes.router)


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
    return {"status": "healthy"}