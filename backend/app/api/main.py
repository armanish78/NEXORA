from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.dependencies import init_core_brain
from app.api.routes import router
from app.database import initialize_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the heavy LLM provider, retriever, and DB
    initialize_db()
    init_core_brain()
    yield
    # Shutdown logic (if any)

app = FastAPI(
    title="Antigravity Core Brain API",
    description="REST interface for the frozen Core Brain",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)
