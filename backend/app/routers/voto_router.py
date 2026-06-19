from fastapi import APIRouter, Depends

from app.services.voto_service import VotoService
from app.dependencies import get_voto_service
from app.schemas.voto_schema import VotoCreate, VotoResponse

router = APIRouter()


# NOTA DE DISEÑO: este router intencionalmente NO tiene PUT ni DELETE.
# Un voto, una vez registrado, es inmutable: permitir editarlo o
# borrarlo comprometería la integridad de cualquier proceso electoral.
# Ver docs/decisiones_diseno.md.


@router.get("", response_model=list[VotoResponse])
def listar_votos(service: VotoService = Depends(get_voto_service)):
    return service.listar_todos()


@router.get("/{voto_id}", response_model=VotoResponse)
def obtener_voto(voto_id: int, service: VotoService = Depends(get_voto_service)):
    return service.obtener_por_id(voto_id)


@router.post("", response_model=VotoResponse, status_code=201)
def registrar_voto(
    datos: VotoCreate,
    cedula: str | None = None,
    service: VotoService = Depends(get_voto_service),
):
    """
    Registra un voto vinculando candidato (o partido) y momento del voto
    — esto cumple el requisito base por sí solo, sin necesidad de cedula.

    El parámetro 'cedula' es OPCIONAL: si se proporciona, activa el
    control de unicidad de voto (una persona no puede votar dos veces),
    implementado como mejora sobre el enunciado base. Ver
    docs/decisiones_diseno.md para la justificación completa. La cédula
    nunca se persiste junto al voto (no existe relación entre Voto y
    Votante) — solo se usa para validar y actualizar el estado del
    votante en la misma transacción.
    """
    return service.registrar_voto(
        candidato_id=datos.candidato_id,
        partido_id=datos.partido_id,
        cedula=cedula,
    )
