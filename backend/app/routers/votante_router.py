from fastapi import APIRouter, Depends

from app.services.votante_service import VotanteService
from app.dependencies import get_votante_service
from app.schemas.votante_schema import (
    VotanteVerificarRequest,
    VotanteVerificarResponse,
)

router = APIRouter()


# NOTA DE DISEÑO: este router intencionalmente NO expone GET /votantes
# ni GET /votantes/{cedula}. La tabla Votante nunca se lista completa
# vía API: eso comprometería el secreto del voto al permitir construir
# el padrón completo de quién ha votado. Ver docs/decisiones_diseno.md.


@router.post("/verificar", response_model=VotanteVerificarResponse)
def verificar_cedula(
    datos: VotanteVerificarRequest,
    service: VotanteService = Depends(get_votante_service),
):
    puede_votar, mensaje = service.verificar(datos.cedula)
    return VotanteVerificarResponse(puede_votar=puede_votar, mensaje=mensaje)
