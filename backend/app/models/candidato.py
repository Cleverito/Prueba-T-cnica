from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Candidato(Base):
    """
    Representa un candidato vinculado a un partido político.

    Reglas de negocio asociadas (ver docs/decisiones_diseno.md):
    - 'numero' es texto (no entero) para soportar formatos como "01A".
    - 'numero' es único SOLO dentro de su propio partido, no globalmente
      (ver UniqueConstraint compuesto abajo).
    - Un candidato siempre pertenece a un partido (partido_id es obligatorio).
    - No se puede eliminar un candidato si tiene votos asociados
      (ON DELETE RESTRICT en la relación con Voto).
    - No se puede eliminar el partido de un candidato existente
      (ON DELETE RESTRICT hacia Partido).
    """

    __tablename__ = "candidatos"
    __table_args__ = (
        UniqueConstraint("partido_id", "numero", name="uq_candidato_partido_numero"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    numero: Mapped[str] = mapped_column(String(10), nullable=False)

    partido_id: Mapped[int] = mapped_column(
        ForeignKey("partidos.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Relación hacia el partido al que pertenece
    partido: Mapped["Partido"] = relationship(back_populates="candidatos")

    # Relación inversa: un candidato puede tener muchos votos
    votos: Mapped[list["Voto"]] = relationship(
        back_populates="candidato",
        passive_deletes=False,
    )

    def __repr__(self) -> str:
        return f"<Candidato id={self.id} nombre={self.nombre!r} numero={self.numero!r}>"
