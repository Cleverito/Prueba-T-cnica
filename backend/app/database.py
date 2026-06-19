from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings


# Motor de conexión a PostgreSQL
engine = create_engine(
    settings.database_url,
    # Pool de conexiones: evita abrir/cerrar una conexión por cada request
    pool_pre_ping=True,      # Verifica que la conexión siga viva antes de usarla
    pool_size=10,            # Conexiones simultáneas mantenidas abiertas
    max_overflow=20,         # Conexiones extra permitidas en picos de carga
)

# Fábrica de sesiones: cada request obtiene su propia sesión
SessionLocal = sessionmaker(
    autocommit=False,   # Las transacciones deben confirmarse explícitamente
    autoflush=False,    # No sincroniza automáticamente antes de cada query
    bind=engine,
)


class Base(DeclarativeBase):
    """Clase base que heredan todos los modelos SQLAlchemy del proyecto."""
    pass


def get_db():
    """
    Dependencia de FastAPI que provee una sesión de BD por request.
    Garantiza que la sesión se cierra siempre, incluso si ocurre una excepción.

    Uso en routers:
        from fastapi import Depends
        from app.database import get_db
        from sqlalchemy.orm import Session

        @router.get("/ejemplo")
        def mi_endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
