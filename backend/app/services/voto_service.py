"""
Service de Voto.

Aquí vive la decisión de diseño más importante del sistema: la regla
de que el partido de un voto debe coincidir con el partido real del
candidato. En vez de validar y rechazar, se construye el voto de forma
que la inconsistencia sea imposible (el cliente nunca envía partido_id
cuando hay candidato_id; este Service lo deriva).

También aplica el patrón Factory Method: _construir_voto() centraliza
la decisión de CÓMO se construye un voto según su tipo (a candidato vs.
a partido directo), en vez de repetir esa lógica condicional en el
router o en cualquier otro lugar que necesite crear un voto.
"""

from sqlalchemy.orm import Session

from app.models.voto import Voto
from app.repositories.voto_repository import VotoRepository
from app.repositories.candidato_repository import CandidatoRepository
from app.repositories.partido_repository import PartidoRepository
from app.services.votante_service import VotanteService
from app.exceptions.dominio_exceptions import RecursoNoEncontrado


class VotoService:
    def __init__(
        self,
        db: Session,
        repository: VotoRepository,
        candidato_repository: CandidatoRepository,
        partido_repository: PartidoRepository,
        votante_service: VotanteService,
    ):
        self.db = db
        self.repository = repository
        self.candidato_repository = candidato_repository
        self.partido_repository = partido_repository
        self.votante_service = votante_service

    def listar_todos(self) -> list[Voto]:
        return self.repository.listar_todos()

    def obtener_por_id(self, voto_id: int) -> Voto:
        voto = self.repository.obtener_por_id(voto_id)
        if voto is None:
            raise RecursoNoEncontrado("Voto", voto_id)
        return voto

    def _construir_voto(
        self, candidato_id: int | None, partido_id: int | None
    ) -> tuple[int, int | None]:
        """
        Factory Method: decide cómo construir los datos de un voto según
        su tipo. Devuelve (partido_id_final, candidato_id_final).

        - Voto a candidato: ignora cualquier partido_id que llegue del
          cliente (el schema VotoCreate ya impide que llegue, pero esta
          función es la garantía definitiva) y lo deriva del candidato.
        - Voto directo a partido: usa el partido_id recibido, valida
          que exista.
        """
        if candidato_id is not None:
            candidato = self.candidato_repository.obtener_por_id(candidato_id)
            if candidato is None:
                raise RecursoNoEncontrado("Candidato", candidato_id)
            # El partido SIEMPRE se deriva del candidato real, nunca del cliente.
            return candidato.partido_id, candidato_id

        # Voto directo a partido (sin candidato)
        partido = self.partido_repository.obtener_por_id(partido_id)
        if partido is None:
            raise RecursoNoEncontrado("Partido", partido_id)
        return partido.id, None

    def registrar_voto(
        self,
        candidato_id: int | None,
        partido_id: int | None,
        cedula: str | None = None,
    ) -> Voto:
        """
        Registra un voto completo.

        El enunciado base solo exige vincular candidato, partido y momento
        del voto — sin mencionar control de identidad del votante. La
        verificación de cédula (control de unicidad / "una persona, un
        voto") se implementó como mejora sobre ese enunciado, justificada
        en docs/decisiones_diseno.md. Para no acoplar el caso base a esa
        mejora, 'cedula' es OPCIONAL aquí:

        - Si se proporciona: se aplica el control completo de unicidad
          (votante debe existir, no haber votado, no estar expirado) y
          la actualización de su estado ocurre en la MISMA transacción
          atómica que la inserción del voto.
        - Si no se proporciona: el voto se registra directamente, sin
          ninguna validación de votante, cumpliendo el enunciado base
          de forma independiente.
        """
        try:
            votante = None
            if cedula is not None:
                # Lanza VotanteNoHabilitado si la cédula ya votó, está
                # bloqueada, o no fue verificada previamente.
                votante = self.votante_service.validar_puede_votar(cedula)

            # Derivar partido_id/candidato_id correctos (Factory Method)
            partido_id_final, candidato_id_final = self._construir_voto(
                candidato_id, partido_id
            )

            # Crear el voto (usa flush, no commit: ver VotoRepository)
            voto = self.repository.crear(
                partido_id=partido_id_final, candidato_id=candidato_id_final
            )

            # Solo si hay votante de por medio, se marca en la misma
            # transacción atómica (flush, no commit, ver VotanteRepository).
            if votante is not None:
                self.votante_service.repository.marcar_como_voto(votante)

            # Confirmar todas las operaciones en una sola transacción
            self.db.commit()

            # Refrescar para traer las relaciones (candidato, partido) completas
            self.db.refresh(voto)
            return voto

        except Exception:
            self.db.rollback()
            raise
