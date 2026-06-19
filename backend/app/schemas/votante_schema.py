from pydantic import BaseModel, Field


class VotanteVerificarRequest(BaseModel):
    """Datos que el cliente envía para verificar/registrar una cédula."""
    cedula: str = Field(..., min_length=1, max_length=20)


class VotanteVerificarResponse(BaseModel):
    """
    Respuesta de la verificación de cédula.

    Importante (ver docs/decisiones_diseno.md): esta respuesta NUNCA
    expone el listado de votantes ni permite recuperar el estado de
    una cédula ajena por fuera de este flujo puntual. Solo informa
    si la cédula que se acaba de consultar puede pasar a votar.
    """
    puede_votar: bool
    mensaje: str
