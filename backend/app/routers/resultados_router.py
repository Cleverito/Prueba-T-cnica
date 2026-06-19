from fastapi import APIRouter, Depends

from app.services.resultados_service import ResultadosService
from app.dependencies import get_resultados_service
from app.schemas.resultados_schema import ResultadosResponse

router = APIRouter()


@router.get("", response_model=ResultadosResponse)
def obtener_resultados(
    service: ResultadosService = Depends(get_resultados_service),
):
    return service.calcular()
