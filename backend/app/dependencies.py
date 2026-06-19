"""
Dependencias de FastAPI reutilizables en los routers.

Centraliza la construcción de la cadena Repository -> Service para
cada entidad. Cada función aquí es una "fábrica" que FastAPI invoca
automáticamente por cada request gracias a Depends(), inyectando
una sesión de base de datos fresca (ver get_db en database.py).

Esto evita repetir "db = Depends(get_db); repo = XRepository(db);
service = XService(repo)" en cada endpoint de cada router.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import (
    PartidoRepository,
    CandidatoRepository,
    VotoRepository,
    VotanteRepository,
)
from app.services import (
    PartidoService,
    CandidatoService,
    VotoService,
    VotanteService,
    ResultadosService,
)


def get_partido_service(db: Session = Depends(get_db)) -> PartidoService:
    return PartidoService(PartidoRepository(db))


def get_candidato_service(db: Session = Depends(get_db)) -> CandidatoService:
    return CandidatoService(CandidatoRepository(db), PartidoRepository(db))


def get_votante_service(db: Session = Depends(get_db)) -> VotanteService:
    return VotanteService(VotanteRepository(db))


def get_voto_service(db: Session = Depends(get_db)) -> VotoService:
    votante_service = VotanteService(VotanteRepository(db))
    return VotoService(
        db=db,
        repository=VotoRepository(db),
        candidato_repository=CandidatoRepository(db),
        partido_repository=PartidoRepository(db),
        votante_service=votante_service,
    )


def get_resultados_service(db: Session = Depends(get_db)) -> ResultadosService:
    return ResultadosService(db)
