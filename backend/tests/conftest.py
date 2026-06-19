"""
Fixtures compartidos para todos los tests.

Decisión técnica: los tests usan SQLite en archivo temporal, no
PostgreSQL real. Esto los hace rápidos y no requieren Docker corriendo
para ejecutarse (útil en CI/CD).

Detalle de implementación importante: se parchea sqlalchemy.create_engine
ANTES de cualquier importación de app.*, en el nivel de módulo de este
archivo (no dentro de una función), porque app.database crea su engine
en el momento de ser importado (efecto de import-time). Si el parche
ocurre después de la primera importación, los modelos ya quedaron
registrados contra un engine apuntando a PostgreSQL falso.
"""

import os
import tempfile

import pytest
import sqlalchemy

# ── Parche aplicado a nivel de módulo, antes de importar app.* ──
os.environ["DATABASE_URL"] = "postgresql://fake:fake@localhost/fake"
os.environ["TIEMPO_LIMITE_VOTO_MINUTOS"] = "5"

_TEST_DB_PATH = tempfile.mktemp(suffix=".db")
_original_create_engine = sqlalchemy.create_engine


def _patched_create_engine(url, **kwargs):
    return _original_create_engine(f"sqlite:///{_TEST_DB_PATH}")


sqlalchemy.create_engine = _patched_create_engine

# Ahora sí, importar la app: usará el engine de SQLite parcheado arriba
from app.main import app  # noqa: E402
from app.database import Base, engine  # noqa: E402


@pytest.fixture()
def client():
    """
    Proporciona un TestClient con la base de datos recreada limpia
    antes de CADA test (aislamiento total entre tests).
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    os.makedirs("static/logos", exist_ok=True)

    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client
