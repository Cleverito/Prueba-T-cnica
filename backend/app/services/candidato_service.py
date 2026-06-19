"""
Service de Candidato.
"""

from app.models.candidato import Candidato
from app.repositories.candidato_repository import CandidatoRepository
from app.repositories.partido_repository import PartidoRepository
from app.exceptions.dominio_exceptions import (
    RecursoNoEncontrado,
    RecursoDuplicado,
    OperacionNoPermitida,
)


class CandidatoService:
    def __init__(
        self,
        repository: CandidatoRepository,
        partido_repository: PartidoRepository,
    ):
        self.repository = repository
        self.partido_repository = partido_repository

    def listar_todos(self) -> list[Candidato]:
        return self.repository.listar_todos()

    def obtener_por_id(self, candidato_id: int) -> Candidato:
        candidato = self.repository.obtener_por_id(candidato_id)
        if candidato is None:
            raise RecursoNoEncontrado("Candidato", candidato_id)
        return candidato

    def _validar_partido_existe(self, partido_id: int) -> None:
        if self.partido_repository.obtener_por_id(partido_id) is None:
            raise RecursoNoEncontrado("Partido", partido_id)

    def _validar_numero_disponible(
        self, partido_id: int, numero: str, candidato_id_actual: int | None = None
    ) -> None:
        """
        Valida la unicidad compuesta (partido_id, numero). Si se está
        actualizando un candidato existente, se excluye su propio id
        de la comprobación (de lo contrario, un candidato "chocaría"
        consigo mismo al no cambiar su número).
        """
        existente = self.repository.obtener_por_partido_y_numero(partido_id, numero)
        if existente is not None and existente.id != candidato_id_actual:
            raise RecursoDuplicado(
                "Candidato",
                "numero",
                f"{numero} (en partido {partido_id})",
            )

    def crear(self, nombre: str, numero: str, partido_id: int) -> Candidato:
        self._validar_partido_existe(partido_id)
        self._validar_numero_disponible(partido_id, numero)
        return self.repository.crear(nombre=nombre, numero=numero, partido_id=partido_id)

    def actualizar(
        self, candidato_id: int, nombre: str, numero: str, partido_id: int
    ) -> Candidato:
        candidato = self.obtener_por_id(candidato_id)
        self._validar_partido_existe(partido_id)
        self._validar_numero_disponible(partido_id, numero, candidato_id_actual=candidato_id)
        return self.repository.actualizar(
            candidato, nombre=nombre, numero=numero, partido_id=partido_id
        )

    def eliminar(self, candidato_id: int) -> None:
        candidato = self.obtener_por_id(candidato_id)

        if self.repository.tiene_votos(candidato_id):
            raise OperacionNoPermitida(
                mensaje=(
                    f"No se puede eliminar al candidato '{candidato.nombre}' "
                    "porque ya tiene votos registrados"
                ),
                detalles={"candidato_id": candidato_id, "candidato_nombre": candidato.nombre},
            )

        self.repository.eliminar(candidato)
