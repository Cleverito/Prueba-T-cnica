from app.schemas.partido_schema import PartidoCreate, PartidoUpdate, PartidoResponse
from app.schemas.candidato_schema import CandidatoCreate, CandidatoUpdate, CandidatoResponse
from app.schemas.voto_schema import VotoCreate, VotoResponse
from app.schemas.votante_schema import VotanteVerificarRequest, VotanteVerificarResponse
from app.schemas.resultados_schema import ResultadoCandidato, ResultadoPartido, ResultadosResponse

__all__ = [
    "PartidoCreate", "PartidoUpdate", "PartidoResponse",
    "CandidatoCreate", "CandidatoUpdate", "CandidatoResponse",
    "VotoCreate", "VotoResponse",
    "VotanteVerificarRequest", "VotanteVerificarResponse",
    "ResultadoCandidato", "ResultadoPartido", "ResultadosResponse",
]
