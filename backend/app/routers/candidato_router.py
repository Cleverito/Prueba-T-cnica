from fastapi import APIRouter, Depends

from app.services.candidato_service import CandidatoService
from app.dependencies import get_candidato_service
from app.schemas.candidato_schema import (
    CandidatoCreate,
    CandidatoUpdate,
    CandidatoResponse,
)

router = APIRouter()


@router.get("", response_model=list[CandidatoResponse])
def listar_candidatos(service: CandidatoService = Depends(get_candidato_service)):
    return service.listar_todos()


@router.get("/{candidato_id}", response_model=CandidatoResponse)
def obtener_candidato(
    candidato_id: int, service: CandidatoService = Depends(get_candidato_service)
):
    return service.obtener_por_id(candidato_id)


@router.post("", response_model=CandidatoResponse, status_code=201)
def crear_candidato(
    datos: CandidatoCreate, service: CandidatoService = Depends(get_candidato_service)
):
    return service.crear(
        nombre=datos.nombre, numero=datos.numero, partido_id=datos.partido_id
    )


@router.put("/{candidato_id}", response_model=CandidatoResponse)
def actualizar_candidato(
    candidato_id: int,
    datos: CandidatoUpdate,
    service: CandidatoService = Depends(get_candidato_service),
):
    return service.actualizar(
        candidato_id,
        nombre=datos.nombre,
        numero=datos.numero,
        partido_id=datos.partido_id,
    )


@router.delete("/{candidato_id}", status_code=200)
def eliminar_candidato(
    candidato_id: int, service: CandidatoService = Depends(get_candidato_service)
):
    service.eliminar(candidato_id)
    return {"mensaje": "Candidato eliminado correctamente"}
