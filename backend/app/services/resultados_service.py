"""
Service de Resultados.

A diferencia de los otros services, este no corresponde a una tabla
propia: construye una vista agregada (conteos) a partir de Partido,
Candidato y Voto. Usa SQL de agregación (GROUP BY/COUNT) en vez de
traer todos los votos a Python y contarlos ahí, por eficiencia.
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.partido import Partido
from app.models.candidato import Candidato
from app.models.voto import Voto


class ResultadosService:
    def __init__(self, db: Session):
        self.db = db

    def calcular(self) -> dict:
        partidos = self.db.query(Partido).order_by(Partido.id).all()

        # Conteo de votos por candidato: una sola query agregada
        conteo_por_candidato = dict(
            self.db.query(Voto.candidato_id, func.count(Voto.id))
            .filter(Voto.candidato_id.isnot(None))
            .group_by(Voto.candidato_id)
            .all()
        )

        # Conteo de votos directos a partido (sin candidato): otra query agregada
        conteo_directo_por_partido = dict(
            self.db.query(Voto.partido_id, func.count(Voto.id))
            .filter(Voto.candidato_id.is_(None))
            .group_by(Voto.partido_id)
            .all()
        )

        por_partido = []
        total_votos = 0

        for partido in partidos:
            candidatos_resultado = []
            votos_candidatos_partido = 0

            for candidato in partido.candidatos:
                votos_candidato = conteo_por_candidato.get(candidato.id, 0)
                votos_candidatos_partido += votos_candidato
                candidatos_resultado.append(
                    {
                        "candidato_id": candidato.id,
                        "candidato_nombre": candidato.nombre,
                        "numero": candidato.numero,
                        "votos": votos_candidato,
                    }
                )

            votos_directos = conteo_directo_por_partido.get(partido.id, 0)
            votos_totales_partido = votos_candidatos_partido + votos_directos
            total_votos += votos_totales_partido

            por_partido.append(
                {
                    "partido_id": partido.id,
                    "partido_nombre": partido.nombre,
                    "votos_totales": votos_totales_partido,
                    "votos_directos_partido": votos_directos,
                    "candidatos": candidatos_resultado,
                }
            )

        return {"total_votos": total_votos, "por_partido": por_partido}
