import gc
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool
from pydantic import ValidationError

try:
    from fastapi_cache import FastAPICache
    from fastapi_cache.backends.redis import RedisBackend
except ImportError:
    FastAPICache = None
    RedisBackend = None

try:
    from fastapi_limiter import FastAPILimiter
except ImportError:
    FastAPILimiter = None

try:
    from jose import jwt
except ImportError:
    import jwt

from app.api.v1.api import api_router as api_router_v1
from app.api.deps import get_redis_client
from app.core import security
from app.core.config import ModeEnum, settings
from app.utils.fastapi_globals import GlobalsMiddleware

logger = logging.getLogger(__name__)


async def user_id_identifier(request: Request):
    if request.scope["type"] == "http":
        auth_header = request.headers.get("Authorization")
        if auth_header is not None:
            header_parts = auth_header.split()
            if len(header_parts) == 2 and header_parts[0].lower() == "bearer":
                token = header_parts[1]
                try:
                    payload = jwt.decode(
                        token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
                    )
                    return payload["sub"]
                except (jwt.JWTError, ValidationError):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Could not validate credentials",
                    )

    if request.scope["type"] == "websocket":
        return request.scope["path"]

    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]

    client = request.client
    ip = getattr(client, "host", "0.0.0.0")
    return ip + ":" + request.scope["path"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if FastAPICache and FastAPILimiter:
        try:
            redis_client = await get_redis_client()
            FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
            await FastAPILimiter.init(redis_client, identifier=user_id_identifier)
            logger.info("Redis cache and rate limiter initialized")
        except Exception as e:
            logger.warning(f"Could not connect to Redis during startup: {e}")

    yield

    # Shutdown
    if FastAPICache and FastAPILimiter:
        try:
            await FastAPICache.clear()
            await FastAPILimiter.close()
        except Exception:
            pass
    gc.collect()


# Core Application Instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    SQLAlchemyMiddleware,
    db_url=settings.ASYNC_DATABASE_URI,
    engine_args={
        "echo": False,
        "poolclass": NullPool
        if settings.MODE == ModeEnum.testing
        else AsyncAdaptedQueuePool,
    },
)
app.add_middleware(GlobalsMiddleware)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/docs")


# Include Consolidated API Router
app.include_router(api_router_v1, prefix=settings.API_V1_STR)

# Add pagination support
add_pagination(app)
