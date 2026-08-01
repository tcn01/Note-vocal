from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.redis import close_redis, init_redis

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await init_redis()
    yield
    await close_redis()


app = FastAPI(
    title="VisionNest API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount thư mục static để phục vụ file audio TTS
static_dir = Path(settings.STATIC_DIR)
static_dir.mkdir(parents=True, exist_ok=True)
(static_dir / "audio").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

app.include_router(api_router, prefix=settings.API_V1_STR)
