"""Tests del endpoint de resultados agregados."""


def test_resultados_vacios_sin_votos(client):
    client.post("/partidos", json={"nombre": "Partido Verde"})

    r = client.get("/resultados")
    assert r.status_code == 200
    data = r.json()
    assert data["total_votos"] == 0


def test_resultados_separan_votos_directos_de_candidatos(client):
    """
    Caso central del diseño de /resultados: un partido puede acumular
    votos tanto de sus candidatos como de votos directos (sin
    candidato), y el endpoint debe reportar ambos correctamente.
    """
    partido = client.post("/partidos", json={"nombre": "Partido Verde"}).json()
    candidato = client.post(
        "/candidatos",
        json={"nombre": "Ana Pérez", "numero": "01A", "partido_id": partido["id"]},
    ).json()

    # Un voto al candidato
    client.post("/votantes/verificar", json={"cedula": "1000000001"})
    client.post("/votos?cedula=1000000001", json={"candidato_id": candidato["id"]})

    # Un voto directo al partido
    client.post("/votantes/verificar", json={"cedula": "1000000002"})
    client.post("/votos?cedula=1000000002", json={"partido_id": partido["id"]})

    r = client.get("/resultados")
    data = r.json()

    assert data["total_votos"] == 2
    resultado_partido = data["por_partido"][0]
    assert resultado_partido["votos_totales"] == 2
    assert resultado_partido["votos_directos_partido"] == 1
    assert resultado_partido["candidatos"][0]["votos"] == 1
