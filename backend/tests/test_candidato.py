"""Tests del CRUD de Candidato, con énfasis en la unicidad compuesta."""


def _crear_partido(client, nombre="Partido Verde"):
    return client.post("/partidos", json={"nombre": nombre}).json()


def test_crear_candidato(client):
    partido = _crear_partido(client)

    r = client.post(
        "/candidatos",
        json={"nombre": "Ana Pérez", "numero": "01A", "partido_id": partido["id"]},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["nombre"] == "Ana Pérez"
    assert data["numero"] == "01A"
    # El partido viene anidado completo, no solo el id (decisión de diseño)
    assert data["partido"]["nombre"] == "Partido Verde"


def test_crear_candidato_con_partido_inexistente_da_404(client):
    r = client.post(
        "/candidatos",
        json={"nombre": "Ana Pérez", "numero": "01A", "partido_id": 999},
    )
    assert r.status_code == 404
    assert r.json()["error"]["codigo"] == "RECURSO_NO_ENCONTRADO"


def test_mismo_numero_en_mismo_partido_falla(client):
    """Unicidad compuesta: (partido_id, numero) no puede repetirse."""
    partido = _crear_partido(client)
    client.post(
        "/candidatos",
        json={"nombre": "Ana Pérez", "numero": "01A", "partido_id": partido["id"]},
    )

    r = client.post(
        "/candidatos",
        json={"nombre": "Otro Candidato", "numero": "01A", "partido_id": partido["id"]},
    )
    assert r.status_code == 409
    assert r.json()["error"]["codigo"] == "RECURSO_DUPLICADO"


def test_mismo_numero_en_partidos_distintos_es_valido(client):
    """
    Unicidad compuesta: el mismo número PUEDE repetirse si los
    candidatos pertenecen a partidos diferentes.
    """
    partido1 = _crear_partido(client, "Partido Verde")
    partido2 = _crear_partido(client, "Partido Azul")

    r1 = client.post(
        "/candidatos",
        json={"nombre": "Ana Pérez", "numero": "01A", "partido_id": partido1["id"]},
    )
    r2 = client.post(
        "/candidatos",
        json={"nombre": "Luis Gómez", "numero": "01A", "partido_id": partido2["id"]},
    )

    assert r1.status_code == 201
    assert r2.status_code == 201


def test_eliminar_candidato_con_votos_falla(client):
    partido = _crear_partido(client)
    candidato = client.post(
        "/candidatos",
        json={"nombre": "Ana Pérez", "numero": "01A", "partido_id": partido["id"]},
    ).json()

    client.post("/votantes/verificar", json={"cedula": "1000000001"})
    client.post(
        "/votos?cedula=1000000001", json={"candidato_id": candidato["id"]}
    )

    r = client.delete(f"/candidatos/{candidato['id']}")
    assert r.status_code == 409
    assert r.json()["error"]["codigo"] == "OPERACION_NO_PERMITIDA"
