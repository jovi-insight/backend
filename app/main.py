from contextlib import asynccontextmanager
from typing import AsyncGenerator
import asyncio

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.core.database import init_db, SessionLocal
from app.core.seed import seed_materias
from app.core import cache
from app.routers import ia, conteudo, dashboard, pastas, materias


async def _limpar_cache_periodicamente():
    """Limpa imagens expiradas do cache a cada 60 segundos."""
    while True:
        await asyncio.sleep(60)
        cache.limpar_expirados()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Inicializa recursos no startup e libera no shutdown."""
    init_db()
    db = SessionLocal()
    try:
        seed_materias(db)
    finally:
        db.close()
    task = asyncio.create_task(_limpar_cache_periodicamente())
    yield
    task.cancel()


app = FastAPI(
    title="JOVI API",
    description="API de produtividade estudantil",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(ia.router)
app.include_router(conteudo.router)
app.include_router(dashboard.router)
app.include_router(pastas.router)
app.include_router(materias.router)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/scalar", include_in_schema=False)
async def scalar_docs():
    return HTMLResponse(
        """
<!DOCTYPE html>
<html>
<head>
    <title>JOVI API - Scalar</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>body { margin: 0; }</style>
</head>
<body>
    <div id="app"></div>
    <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
    <script>
        Scalar.createApiReference('#app', { url: '/openapi.json' })
    </script>
</body>
</html>
"""
    )
