"""
Repository de Voto.

Responsabilidad única: leer y escribir votos. NO contiene la regla de
derivar partido_id desde el candidato (eso vive en VotoService) ni
sabe nada sobre el estado de los votantes (eso vive en VotanteService).
"""

from sqlalchemy.orm import Session, joinedload

from app.models.voto import Voto


class VotoRepository:
    def __init__(self, db: Session):
        self.db = db

    def listar_todos(self) -> list[Voto]:
        return (
            self.db.query(Voto)
            .options(joinedload(Voto.candidato), joinedload(Voto.partido))
            .order_by(Voto.id)
            .all()
        )

    def obtener_por_id(self, voto_id: int) -> Voto | None:
        return (
            self.db.query(Voto)
            .options(joinedload(Voto.candidato), joinedload(Voto.partido))
            .filter(Voto.id == voto_id)
            .first()
        )

    def crear(self, partido_id: int, candidato_id: int | None = None) -> Voto:
        """
        Crea un voto. Quien llama (VotoService) es responsable de haber
        derivado partido_id correctamente cuando hay candidato_id, y de
        envolver esta llamada junto con la actualización del Votante
        en una única transacción atómica (ver VotoService).
        """
        voto = Voto(partido_id=partido_id, candidato_id=candidato_id)
        self.db.add(voto)
        self.db.flush()  # Asigna el id sin cerrar la transacción todavía
        return voto
