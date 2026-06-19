"""
Service de Partido.

Orquesta las reglas de negocio sobre partidos, usando PartidoRepository
para el acceso a datos. Traduce situaciones del dominio a excepciones
de dominio (RecursoNoEncontrado, RecursoDuplicado, OperacionNoPermitida),
que luego exception_handlers.py traduce a HTTP.
"""

from app.models.partido import Partido
from app.repositories.partido_repository import PartidoRepository
from app.exceptions.dominio_exceptions import (
    RecursoNoEncontrado,
    RecursoDuplicado,
    OperacionNoPermitida,
)


class PartidoService:
    def __init__(self, repository: PartidoRepository):
        self.repository = repository

    def listar_todos(self) -> list[Partido]:
        return self.repository.listar_todos()

    def obtener_por_id(self, partido_id: int) -> Partido:
        partido = self.repository.obtener_por_id(partido_id)
        if partido is None:
            raise RecursoNoEncontrado("Partido", partido_id)
        return partido

    def crear(self, nombre: str) -> Partido:
        if self.repository.obtener_por_nombre(nombre) is not None:
            raise RecursoDuplicado("Partido", "nombre", nombre)
        return self.repository.crear(nombre=nombre)

    def actualizar(self, partido_id: int, nombre: str) -> Partido:
        partido = self.obtener_por_id(partido_id)  # lanza RecursoNoEncontrado si no existe

        existente = self.repository.obtener_por_nombre(nombre)
        if existente is not None and existente.id != partido_id:
            raise RecursoDuplicado("Partido", "nombre", nombre)

        return self.repository.actualizar(partido, nombre=nombre)

    def actualizar_logo(self, partido_id: int, logo_url: str) -> Partido:
        partido = self.obtener_por_id(partido_id)
        return self.repository.actualizar_logo(partido, logo_url=logo_url)

    def eliminar(self, partido_id: int) -> None:
        partido = self.obtener_por_id(partido_id)

        if self.repository.tiene_candidatos(partido_id):
            raise OperacionNoPermitida(
                mensaje=(
                    f"No se puede eliminar el partido '{partido.nombre}' "
                    "porque tiene candidatos asociados"
                ),
                detalles={"partido_id": partido_id, "partido_nombre": partido.nombre},
            )

        self.repository.eliminar(partido)
