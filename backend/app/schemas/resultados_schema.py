from pydantic import BaseModel


class ResultadoCandidato(BaseModel):
    """Conteo de votos de un candidato dentro de un partido."""
    candidato_id: int
    candidato_nombre: str
    numero: str
    votos: int


class ResultadoPartido(BaseModel):
    """
    Conteo de votos de un partido: incluye el detalle de cada candidato
    y los votos directos al partido (sin candidato específico).
    """
    partido_id: int
    partido_nombre: str
    votos_totales: int               # candidatos + votos_directos_partido
    votos_directos_partido: int      # votos sin candidato_id
    candidatos: list[ResultadoCandidato]


class ResultadosResponse(BaseModel):
    """Respuesta completa del endpoint GET /resultados."""
    total_votos: int
    por_partido: list[ResultadoPartido]
