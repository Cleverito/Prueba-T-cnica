"""
Repository de Partido.

Responsabilidad única: leer y escribir partidos en la base de datos.
NO contiene reglas de negocio (eso vive en PartidoService). Por ejemplo,
este repository no decide si un nombre duplicado es un error: solo
intenta el INSERT y deja que la capa de Service interprete el resultado.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.partido import Partido


class PartidoRepository:
    def __init__(self, db: Session):
        self.db = db

    def listar_todos(self) -> list[Partido]:
        return self.db.query(Partido).order_by(Partido.id).all()

    def obtener_por_id(self, partido_id: int) -> Partido | None:
        return self.db.query(Partido).filter(Partido.id == partido_id).first()

    def obtener_por_nombre(self, nombre: str) -> Partido | None:
        return self.db.query(Partido).filter(Partido.nombre == nombre).first()

    def crear(self, nombre: str, logo_url: str | None = None) -> Partido:
        partido = Partido(nombre=nombre, logo_url=logo_url)
        self.db.add(partido)
        self.db.commit()
        self.db.refresh(partido)
        return partido

    def actualizar(self, partido: Partido, nombre: str) -> Partido:
        partido.nombre = nombre
        self.db.commit()
        self.db.refresh(partido)
        return partido

    def actualizar_logo(self, partido: Partido, logo_url: str) -> Partido:
        partido.logo_url = logo_url
        self.db.commit()
        self.db.refresh(partido)
        return partido

    def tiene_candidatos(self, partido_id: int) -> bool:
        """
        Verifica si el partido tiene candidatos asociados, ANTES de
        intentar borrar. Esto permite que el Service lance una excepción
        de dominio clara (OperacionNoPermitida) en vez de depender de
        que PostgreSQL rechace el DELETE con un error críptico de FK.
        """
        from app.models.candidato import Candidato
        return (
            self.db.query(Candidato)
            .filter(Candidato.partido_id == partido_id)
            .first()
            is not None
        )

    def eliminar(self, partido: Partido) -> None:
        """
        Elimina el partido. Si por alguna razón el chequeo previo
        (tiene_candidatos) no se hizo y la BD rechaza el DELETE por la
        restricción ON DELETE RESTRICT, propaga IntegrityError para que
        el Service la traduzca a OperacionNoPermitida igualmente.
        """
        self.db.delete(partido)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
