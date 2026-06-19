"""Tests de Votante."""


def test_verificar_cedula_nueva_permite_votar(client):
    r = client.post("/votantes/verificar", json={"cedula": "1000000001"})

    assert r.status_code == 200
    data = r.json()
    assert data["puede_votar"] is True


def test_verificar_cedula_que_ya_voto_no_permite_votar(client):
    partido = client.post("/partidos", json={"nombre": "Partido Verde"}).json()
    client.post("/votantes/verificar", json={"cedula": "1000000001"})
    client.post("/votos?cedula=1000000001", json={"partido_id": partido["id"]})

    r = client.post("/votantes/verificar", json={"cedula": "1000000001"})

    assert r.status_code == 200
    data = r.json()
    assert data["puede_votar"] is False


def test_no_existe_endpoint_para_listar_votantes():
    """
    Verificación estructural: nunca debe existir un GET que liste
    todas las cédulas (eso comprometería el secreto del voto).
    """
    from app.routers.votante_router import router

    rutas = [route.path for route in router.routes]
    assert "" not in rutas  # No hay GET /votantes (listado completo)
    assert "/{cedula}" not in rutas  # No hay GET /votantes/{cedula}
