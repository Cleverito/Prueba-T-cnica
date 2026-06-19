"""
Repository de Candidato.

Responsabilidad única: leer y escribir candidatos en la base de datos.
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.models.candidato import Candidato


class CandidatoRepository:
    def __init__(self, db: Session):
        self.db = db

    def listar_todos(self) -> list[Candidato]:
        # joinedload precarga el Partido relacionado en la misma query
        # (evita el problema N+1: una query por candidato para traer su partido)
        return (
            self.db.query(Candidato)
            .options(joinedload(Candidato.partido))
            .order_by(Candidato.id)
            .all()
        )

    def obtener_por_id(self, candidato_id: int) -> Candidato | None:
        return (
            self.db.query(Candidato)
            .options(joinedload(Candidato.partido))
            .filter(Candidato.id == candidato_id)
            .first()
        )

    def existe_numero_en_partido(self, partido_id: int, numero: str) -> bool:
        return (
            self.db.query(Candidato)
            .filter(Candidato.partido_id == partido_id, Candidato.numero == numero)
            .first()
            is not None
        )

    def obtener_por_partido_y_numero(self, partido_id: int, numero: str) -> Candidato | None:
        """Usado al validar unicidad compuesta, para excluir el propio id en updates."""
        return (
            self.db.query(Candidato)
            .filter(Candidato.partido_id == partido_id, Candidato.numero == numero)
            .first()
        )

    def crear(self, nombre: str, numero: str, partido_id: int) -> Candidato:
        candidato = Candidato(nombre=nombre, numero=numero, partido_id=partido_id)
        self.db.add(candidato)
        self.db.commit()
        self.db.refresh(candidato)
        return candidato

    def actualizar(
        self, candidato: Candidato, nombre: str, numero: str, partido_id: int
    ) -> Candidato:
        candidato.nombre = nombre
        candidato.numero = numero
        candidato.partido_id = partido_id
        self.db.commit()
        self.db.refresh(candidato)
        return candidato

    def tiene_votos(self, candidato_id: int) -> bool:
        """Verifica si el candidato tiene votos asociados, antes de borrar."""
        from app.models.voto import Voto
        return (
            self.db.query(Voto).filter(Voto.candidato_id == candidato_id).first()
            is not None
        )

    def eliminar(self, candidato: Candidato) -> None:
        self.db.delete(candidato)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise