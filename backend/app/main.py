from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base

# Importar todos los modelos para que SQLAlchemy los registre antes de crear tablas
from app.models import partido, candidato, voto, votante  # noqa: F401

# Importar routers
from app.routers import (
    partido_router,
    candidato_router,
    voto_router,
    votante_router,
    resultados_router,
)

# Importar manejadores de excepciones centralizados
from app.exceptions.exception_handlers import registrar_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código de inicio (antes reemplazaba a @app.on_event("startup"))
    Base.metadata.create_all(bind=engine)
    yield
    # Código de cierre (si se necesitara liberar recursos al apagar)


# ─────────────────────────────────────────
# Instancia principal de la aplicación
# ─────────────────────────────────────────
app = FastAPI(
    title="Sistema Electoral",
    description="API REST para registro y consulta de información electoral.",
    version="1.0.0",
    lifespan=lifespan,
    # Swagger UI disponible en /docs, ReDoc en /redoc
)


# ─────────────────────────────────────────
# Middleware: CORS
# Permite que React (corriendo en otro puerto) consuma la API
# ─────────────────────────────────────────
origins = [
    "http://localhost:3000",    # React en desarrollo local
    "http://localhost:5173",    # Vite (alternativa a CRA)
]

if settings.environment == "production":
    # En producción (Railway), agregar la URL pública del frontend
    # Esto se configura vía variable de entorno FRONTEND_URL en Railway
    import os
    frontend_url = os.getenv("FRONTEND_URL", "")
    if frontend_url:
        origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────
# Archivos estáticos (logos de partidos)
# ─────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")


# ─────────────────────────────────────────
# Manejadores de excepciones centralizados
# ─────────────────────────────────────────
registrar_handlers(app)


# ─────────────────────────────────────────
# Routers
# ─────────────────────────────────────────
app.include_router(partido_router.router, prefix="/partidos", tags=["Partidos"])
app.include_router(candidato_router.router, prefix="/candidatos", tags=["Candidatos"])
app.include_router(voto_router.router, prefix="/votos", tags=["Votos"])
app.include_router(votante_router.router, prefix="/votantes", tags=["Votantes"])
app.include_router(resultados_router.router, prefix="/resultados", tags=["Resultados"])


# ─────────────────────────────────────────
# Health check (útil para Railway y Docker)
# ─────────────────────────────────────────
@app.get("/health", tags=["Sistema"])
def health_check():
    return {"status": "ok", "environment": settings.environment}
