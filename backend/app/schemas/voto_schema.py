from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.partido_schema import PartidoResponse
from app.schemas.candidato_schema import CandidatoResponse


class VotoCreate(BaseModel):
    """
    Datos que el cliente envía para registrar un voto.

    Regla de uso (ver docs/decisiones_diseno.md):
    - Si el voto es a un candidato específico: enviar candidato_id,
      NUNCA partido_id. El backend deriva el partido automáticamente
      a partir del candidato, eliminando por construcción la posibilidad
      de que candidato y partido queden inconsistentes.
    - Si el voto es directo a un partido (sin candidato): enviar
      partido_id, y dejar candidato_id en None.
    - Enviar ambos, o ninguno, es un error de validación (ver más abajo).
    """
    candidato_id: int | None = Field(default=None)
    partido_id: int | None = Field(default=None)

    @model_validator(mode="after")
    def validar_exclusividad(self):
        """
        Garantiza que el cliente especifique exactamente una intención de voto:
        - candidato_id solo (el partido se deriva en el backend), o
        - partido_id solo (voto directo a partido).
        Nunca ambos, nunca ninguno.
        """
        tiene_candidato = self.candidato_id is not None
        tiene_partido = self.partido_id is not None

        if tiene_candidato and tiene_partido:
            raise ValueError(
                "Debe especificar candidato_id O partido_id, no ambos. "
                "El partido se deriva automáticamente cuando se vota por un candidato."
            )
        if not tiene_candidato and not tiene_partido:
            raise ValueError(
                "Debe especificar candidato_id o partido_id para registrar el voto."
            )
        return self


class VotoResponse(BaseModel):
    """
    Forma en la que se devuelve un voto al cliente.
    Nunca incluye información de votante (cédula): esa relación no existe
    en el modelo de datos, por diseño, para preservar el secreto del voto.
    """
    id: int
    candidato: CandidatoResponse | None = None
    partido: PartidoResponse
    hora_voto: datetime

    model_config = ConfigDict(from_attributes=True)
