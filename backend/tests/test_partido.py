"""Tests del CRUD de Partido."""


def test_crear_partido(client):
    r = client.post("/partidos", json={"nombre": "Partido Verde"})
    assert r.status_code == 201
    data = r.json()
    assert data["nombre"] == "Partido Verde"
    assert data["logo_url"] is None
    assert "id" in data


def test_crear_partido_duplicado_falla(client):
    client.post("/partidos", json={"nombre": "Partido Verde"})
    r = client.post("/partidos", json={"nombre": "Partido Verde"})

    assert r.status_code == 409
    assert r.json()["error"]["codigo"] == "RECURSO_DUPLICADO"


def test_listar_partidos(client):
    client.post("/partidos", json={"nombre": "Partido Verde"})
    client.post("/partidos", json={"nombre": "Partido Azul"})

    r = client.get("/partidos")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_obtener_partido_por_id(client):
    creado = client.post("/partidos", json={"nombre": "Partido Verde"}).json()

    r = client.get(f"/partidos/{creado['id']}")
    assert r.status_code == 200
    assert r.json()["nombre"] == "Partido Verde"


def test_obtener_partido_inexistente_da_404(client):
    r = client.get("/partidos/999")
    assert r.status_code == 404
    assert r.json()["error"]["codigo"] == "RECURSO_NO_ENCONTRADO"


def test_actualizar_partido(client):
    creado = client.post("/partidos", json={"nombre": "Partido Verde"}).json()

    r = client.put(f"/partidos/{creado['id']}", json={"nombre": "Partido Verde Renovado"})
    assert r.status_code == 200
    assert r.json()["nombre"] == "Partido Verde Renovado"


def test_eliminar_partido_sin_candidatos(client):
    creado = client.post("/partidos", json={"nombre": "Partido Verde"}).json()

    r = client.delete(f"/partidos/{creado['id']}")
    assert r.status_code == 200

    # Confirmar que ya no existe
    r2 = client.get(f"/partidos/{creado['id']}")
    assert r2.status_code == 404


def test_eliminar_partido_con_candidatos_falla(client):
    """
    Regla de negocio crítica: no se puede eliminar un partido que
    tiene candidatos asociados (protección de integridad electoral).
    """
    partido = client.post("/partidos", json={"nombre": "Partido Verde"}).json()
    client.post(
        "/candidatos",
        json={"nombre": "Ana Pérez", "numero": "01A", "partido_id": partido["id"]},
    )

    r = client.delete(f"/partidos/{partido['id']}")
    assert r.status_code == 409
    assert r.json()["error"]["codigo"] == "OPERACION_NO_PERMITIDA"
