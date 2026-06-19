from pydantic import BaseModel, ConfigDict, Field

from app.schemas.partido_schema import PartidoResponse


class CandidatoCreate(BaseModel):
    """Datos requeridos para crear un candidato."""
    nombre: str = Field(..., min_length=1, max_length=150)
    numero: str = Field(..., min_length=1, max_length=10)
    partido_id: int


class CandidatoUpdate(BaseModel):
    """Datos permitidos al actualizar un candidato."""
    nombre: str = Field(..., min_length=1, max_length=150)
    numero: str = Field(..., min_length=1, max_length=10)
    partido_id: int


class CandidatoResponse(BaseModel):
    """
    Forma en la que se devuelve un candidato al cliente.
    Incluye el objeto Partido completo anidado (no solo partido_id),
    para que el frontend pueda mostrar nombre y logo sin llamadas adicionales.
    """
    id: int
    nombre: str
    numero: str
    partido: PartidoResponse

    model_config = ConfigDict(from_attributes=True)
