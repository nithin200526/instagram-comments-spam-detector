"""
🛡️ AI Social Media Platform — FastAPI Entrypoint
Mounts static files, includes API routes, loads ML model on startup.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.database import init_db
from backend.model import load_model
from backend.routes import router

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: init DB + load ML model."""
    print("\n🚀 Starting AI Social Media Platform...")
    init_db()
    load_model()
    print("✅ Platform ready!\n")
    yield
    print("👋 Shutting down...")


app = FastAPI(
    title="AI Social Media Platform",
    description="Social media platform with real-time AI spam moderation",
    version="1.0.0",
    lifespan=lifespan,
)

# Mount static files
os.makedirs(os.path.join(STATIC_DIR, "uploads"), exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Include API routes
app.include_router(router)


# ─── Frontend Pages ───────────────────────────────────────────────────────────

@app.get("/")
async def feed_page():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/dashboard")
async def dashboard_page():
    return FileResponse(os.path.join(STATIC_DIR, "dashboard.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
