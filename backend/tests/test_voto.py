"""
Tests de Voto.

Cubren las reglas de negocio más sensibles del sistema:
- Derivación automática del partido a partir del candidato.
- Voto directo a partido (sin candidato).
- Exclusividad: no se permite enviar candidato_id y partido_id juntos,
  ni ninguno de los dos.
- Inmutabilidad: no existen endpoints PUT/DELETE para votos.
"""


def _crear_partido_y_candidato(client):
    partido = client.post("/partidos", json={"nombre": "Partido Verde"}).json()
    candidato = client.post(
        "/candidatos",
        json={"nombre": "Ana Pérez", "numero": "01A", "partido_id": partido["id"]},
    ).json()
    return partido, candidato


def test_votar_por_candidato_deriva_partido_automaticamente(client):
    partido, candidato = _crear_partido_y_candidato(client)
    client.post("/votantes/verificar", json={"cedula": "1000000001"})

    r = client.post(
        "/votos?cedula=1000000001", json={"candidato_id": candidato["id"]}
    )

    assert r.status_code == 201
    voto = r.json()
    assert voto["candidato"]["id"] == candidato["id"]
    # Regla central: el partido se derivó del candidato, sin que el
    # cliente lo haya enviado explícitamente.
    assert voto["partido"]["id"] == partido["id"]


def test_votar_directo_a_partido_sin_candidato(client):
    partido = client.post("/partidos", json={"nombre": "Partido Verde"}).json()
    client.post("/votantes/verificar", json={"cedula": "1000000001"})

    r = client.post(
        "/votos?cedula=1000000001", json={"partido_id": partido["id"]}
    )

    assert r.status_code == 201
    voto = r.json()
    assert voto["candidato"] is None
    assert voto["partido"]["id"] == partido["id"]


def test_enviar_candidato_y_partido_juntos_falla(client):
    """Validación de Pydantic (VotoCreate.validar_exclusividad)."""
    partido, candidato = _crear_partido_y_candidato(client)
    client.post("/votantes/verificar", json={"cedula": "1000000001"})

    r = client.post(
        "/votos?cedula=1000000001",
        json={"candidato_id": candidato["id"], "partido_id": partido["id"]},
    )

    assert r.status_code == 422  # Error de validación de Pydantic


def test_no_enviar_ni_candidato_ni_partido_falla(client):
    client.post("/votantes/verificar", json={"cedula": "1000000001"})

    r = client.post("/votos?cedula=1000000001", json={})

    assert r.status_code == 422


def test_votar_sin_verificar_cedula_falla(client):
    """No se puede votar con una cédula que nunca pasó por /verificar."""
    partido = client.post("/partidos", json={"nombre": "Partido Verde"}).json()

    r = client.post(
        "/votos?cedula=9999999999", json={"partido_id": partido["id"]}
    )

    assert r.status_code == 403
    assert r.json()["error"]["codigo"] == "VOTANTE_NO_HABILITADO"


def test_votar_dos_veces_con_misma_cedula_falla(client):
    partido = client.post("/partidos", json={"nombre": "Partido Verde"}).json()
    client.post("/votantes/verificar", json={"cedula": "1000000001"})
    client.post("/votos?cedula=1000000001", json={"partido_id": partido["id"]})

    r = client.post("/votos?cedula=1000000001", json={"partido_id": partido["id"]})

    assert r.status_code == 403
    assert r.json()["error"]["codigo"] == "VOTANTE_NO_HABILITADO"


def test_listar_votos_no_expone_cedula(client):
    """
    Garantía de secreto del voto: la respuesta de /votos nunca debe
    contener ningún campo relacionado con la cédula del votante.
    """
    partido = client.post("/partidos", json={"nombre": "Partido Verde"}).json()
    client.post("/votantes/verificar", json={"cedula": "1000000001"})
    client.post("/votos?cedula=1000000001", json={"partido_id": partido["id"]})

    r = client.get("/votos")
    assert r.status_code == 200

    cuerpo_completo = str(r.json())
    assert "cedula" not in cuerpo_completo.lower()
    assert "1000000001" not in cuerpo_completo


def test_voto_no_tiene_endpoint_put():
    """
    Verificación estructural: el router de Voto no debe registrar
    una ruta PUT. Esto formaliza en código la decisión de diseño
    de que un voto es inmutable.
    """
    from app.routers.voto_router import router

    metodos_registrados = {
        metodo for route in router.routes for metodo in route.methods
    }
    assert "PUT" not in metodos_registrados
    assert "DELETE" not in metodos_registrados
