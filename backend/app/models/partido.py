from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Partido(Base):
    """
    Representa un partido político participante.

    Reglas de negocio asociadas (ver docs/decisiones_diseno.md):
    - El nombre debe ser único en todo el sistema.
    - El logo es opcional: puede asociarse después de crear el partido.
    - No se puede eliminar un partido si tiene candidatos asociados
      (ver ON DELETE RESTRICT en la relación con Candidato).
    """

    __tablename__ = "partidos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    logo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relación inversa: un partido tiene muchos candidatos.
    # No se usa cascade="all, delete" intencionalmente: queremos que
    # SQLAlchemy/PostgreSQL impidan el borrado si existen candidatos (RESTRICT),
    # no que los borre en cascada.
    candidatos: Mapped[list["Candidato"]] = relationship(
        back_populates="partido",
        passive_deletes=False,
    )

    def __repr__(self) -> str:
        return f"<Partido id={self.id} nombre={self.nombre!r}>"
