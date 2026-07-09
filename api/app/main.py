from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from sqlalchemy import select

from app.config import settings
from app.core.security import hash_password
from app.database import async_session_factory, engine
from app.models.base import Base
from app.models.user import User
from app.routers import admin, agents, auth, dashboard, sync


def get_limiter_key(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    client = request.client
    return client.host if client else "unknown"


limiter = Limiter(key_func=get_limiter_key)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.email == settings.admin_email))
        if not result.scalar_one_or_none():
            session.add(User(
                email=settings.admin_email,
                password_hash=hash_password(settings.admin_password),
                name="Admin",
                role="admin",
            ))
            await session.commit()

    yield
    await engine.dispose()


app = FastAPI(title="RTK Dashboard API", version="0.1.0", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"https://{o}" if o and not o.startswith("http") else o for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    return response


app.include_router(auth.router)
app.include_router(agents.router)
app.include_router(sync.router)
app.include_router(dashboard.router)
app.include_router(admin.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
