"""
Service de Votante.

Aquí vive la lógica de expiración "perezosa" (lazy) que se diseñó:
no hay ningún proceso en segundo plano marcando votantes como
bloqueados. En cada verificación, se calcula en el momento si ya
pasó el tiempo límite desde el registro.
"""

from datetime import datetime, timedelta, timezone

from app.models.votante import Votante, EstadoVotante
from app.repositories.votante_repository import VotanteRepository
from app.config import settings


class VotanteService:
    def __init__(self, repository: VotanteRepository):
        self.repository = repository

    def _esta_expirado(self, votante: Votante) -> bool:
        limite = timedelta(minutes=settings.tiempo_limite_voto_minutos)
        ahora = datetime.now(timezone.utc)

        hora_registro = votante.hora_registro
        # Defensa ante motores/drivers que devuelven datetime "naive"
        # (sin timezone) en vez de "aware". PostgreSQL con
        # DateTime(timezone=True) debería devolver aware siempre, pero
        # esto evita romper el cálculo si el driver no lo garantiza.
        if hora_registro.tzinfo is None:
            hora_registro = hora_registro.replace(tzinfo=timezone.utc)

        return ahora - hora_registro > limite

    def verificar(self, cedula: str) -> tuple[bool, str]:
        """
        Registra la cédula si es nueva, o evalúa su estado actual si ya existe.
        Devuelve (puede_votar, mensaje) en vez de lanzar una excepción,
        porque "no puede votar" es una respuesta válida del dominio,
        no un error del sistema.
        """
        votante = self.repository.obtener_por_cedula(cedula)

        if votante is None:
            self.repository.crear(cedula)
            return True, "Cédula registrada. Puede proceder a votar."

        if votante.estado == EstadoVotante.VOTO:
            return False, "Esta cédula ya emitió su voto."

        if votante.estado == EstadoVotante.PENDIENTE:
            if self._esta_expirado(votante):
                return False, "El tiempo para votar expiró. Esta cédula quedó bloqueada."
            return True, "Puede proceder a votar."

        # estado == BLOQUEADO (si en el futuro se persiste explícitamente)
        return False, "Esta cédula está bloqueada y no puede votar."

    def validar_puede_votar(self, cedula: str) -> Votante:
        """
        Usado por VotoService al momento de registrar un voto real.
        A diferencia de verificar(), aquí SÍ se lanza una excepción de
        dominio si no puede votar, porque en este punto del flujo
        "no puede votar" debe interrumpir la operación de registrar el voto.
        """
        from app.exceptions.dominio_exceptions import VotanteNoHabilitado

        votante = self.repository.obtener_por_cedula(cedula)

        if votante is None:
            raise VotanteNoHabilitado(
                "La cédula no ha sido verificada. Verifique antes de votar."
            )

        if votante.estado == EstadoVotante.VOTO:
            raise VotanteNoHabilitado("Esta cédula ya emitió su voto.")

        if votante.estado == EstadoVotante.PENDIENTE and self._esta_expirado(votante):
            raise VotanteNoHabilitado(
                "El tiempo para votar expiró. Esta cédula quedó bloqueada."
            )

        if votante.estado == EstadoVotante.BLOQUEADO:
            raise VotanteNoHabilitado("Esta cédula está bloqueada y no puede votar.")

        return votante
