"""
Repository de Votante.

Responsabilidad única: leer y escribir el estado de los votantes.
IMPORTANTE: este repository nunca debe usarse para listar cédulas
(no existe un método listar_todos intencionalmente). Cualquier consulta
aquí es puntual, por cédula específica, nunca un volcado completo de
la tabla — eso reforzaría el riesgo de exponer el padrón completo.
"""

from sqlalchemy.orm import Session

from app.models.votante import Votante, EstadoVotante


class VotanteRepository:
    def __init__(self, db: Session):
        self.db = db

    def obtener_por_cedula(self, cedula: str) -> Votante | None:
        return self.db.query(Votante).filter(Votante.cedula == cedula).first()

    def crear(self, cedula: str) -> Votante:
        votante = Votante(cedula=cedula, estado=EstadoVotante.PENDIENTE)
        self.db.add(votante)
        self.db.commit()
        self.db.refresh(votante)
        return votante

    def marcar_como_voto(self, votante: Votante) -> Votante:
        """
        Marca el votante como que ya emitió su voto. Quien llama
        (VotoService) es responsable de ejecutar esto en la MISMA
        transacción que la creación del Voto correspondiente,
        haciendo commit() una sola vez al final de ambas operaciones.
        """
        votante.estado = EstadoVotante.VOTO
        self.db.flush()  # No cierra la transacción: ver VotoService
        return votante
