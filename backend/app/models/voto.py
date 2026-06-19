from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Voto(Base):
    """
    Representa un voto emitido, ya sea hacia un candidato específico
    o directamente hacia un partido (voto en blanco/por lista).

    Reglas de negocio asociadas (ver docs/decisiones_diseno.md):
    - candidato_id es OPCIONAL: permite votos directos a partido.
    - partido_id es SIEMPRE obligatorio, incluso si hay candidato.
    - Si hay candidato, partido_id DEBE coincidir con el partido real
      del candidato. Esta regla NO se valida aquí a nivel de esquema:
      se garantiza en la capa de Service (VotoService), que deriva
      partido_id automáticamente a partir del candidato en vez de
      confiar en lo que envíe el cliente.
    - Un voto es INMUTABLE: no existen endpoints PUT/DELETE para esta
      entidad. Por integridad electoral, un voto no se edita ni se borra
      una vez registrado.
    - NO existe relación alguna con la tabla Votante. Esta ausencia es
      intencional: garantiza el secreto del voto (ver Votante).
    """

    __tablename__ = "votos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    candidato_id: Mapped[int | None] = mapped_column(
        ForeignKey("candidatos.id", ondelete="RESTRICT"),
        nullable=True,
    )
    partido_id: Mapped[int] = mapped_column(
        ForeignKey("partidos.id", ondelete="RESTRICT"),
        nullable=False,
    )

    hora_voto: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    candidato: Mapped["Candidato"] = relationship(back_populates="votos")
    partido: Mapped["Partido"] = relationship()

    def __repr__(self) -> str:
        return f"<Voto id={self.id} candidato_id={self.candidato_id} partido_id={self.partido_id}>"
