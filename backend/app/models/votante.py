from datetime import datetime

from sqlalchemy import String, DateTime, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EstadoVotante:
    """
    Constantes de los estados posibles de un votante.
    Usar estas constantes en vez de strings sueltos evita errores de tipeo
    y centraliza los valores válidos en un solo lugar.
    """
    PENDIENTE = "pendiente"
    VOTO = "voto"
    BLOQUEADO = "bloqueado"

    TODOS = (PENDIENTE, VOTO, BLOQUEADO)


class Votante(Base):
    """
    Registra la cédula de un votante únicamente para controlar que no
    vote más de una vez. NO tiene relación con la tabla Voto.

    Reglas de negocio asociadas (ver docs/decisiones_diseno.md):
    - La cédula es la clave primaria natural (no se usa un id autogenerado).
    - estado tiene 3 valores posibles: pendiente, voto, bloqueado.
    - El bloqueo por expiración de tiempo es "perezoso": no existe un
      proceso en segundo plano que actualice este campo. En su lugar,
      VotanteService calcula en cada consulta si ya pasó el tiempo
      límite (settings.tiempo_limite_voto_minutos) desde hora_registro.
    - Esta tabla NUNCA se expone completa vía API (no hay GET /votantes).
      Solo existe POST /votantes/verificar, que responde con un booleano,
      nunca con el listado de cédulas.
    """

    __tablename__ = "votantes"
    __table_args__ = (
        CheckConstraint(
            f"estado IN {EstadoVotante.TODOS}",
            name="ck_votante_estado_valido",
        ),
    )

    cedula: Mapped[str] = mapped_column(String(20), primary_key=True)

    estado: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=EstadoVotante.PENDIENTE,
        server_default=EstadoVotante.PENDIENTE,
    )

    hora_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Votante cedula={self.cedula!r} estado={self.estado!r}>"
