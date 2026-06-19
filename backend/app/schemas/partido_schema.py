from pydantic import BaseModel, ConfigDict, Field


class PartidoCreate(BaseModel):
    """Datos requeridos para crear un partido. El logo se asocia después (es opcional)."""
    nombre: str = Field(..., min_length=1, max_length=100)


class PartidoUpdate(BaseModel):
    """Datos permitidos al actualizar un partido."""
    nombre: str = Field(..., min_length=1, max_length=100)


class PartidoResponse(BaseModel):
    """Forma en la que se devuelve un partido al cliente."""
    id: int
    nombre: str
    logo_url: str | None = None

    # Permite construir este schema directamente desde un objeto SQLAlchemy
    # (model.Partido) sin convertirlo manualmente a dict primero.
    model_config = ConfigDict(from_attributes=True)
