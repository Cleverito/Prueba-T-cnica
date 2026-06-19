import os
import uuid

from fastapi import APIRouter, Depends, UploadFile, File

from app.services.partido_service import PartidoService
from app.dependencies import get_partido_service
from app.schemas.partido_schema import PartidoCreate, PartidoUpdate, PartidoResponse

router = APIRouter()

LOGOS_DIR = "static/logos"
EXTENSIONES_PERMITIDAS = {".png", ".jpg", ".jpeg", ".svg", ".webp"}


@router.get("", response_model=list[PartidoResponse])
def listar_partidos(service: PartidoService = Depends(get_partido_service)):
    return service.listar_todos()


@router.get("/{partido_id}", response_model=PartidoResponse)
def obtener_partido(
    partido_id: int, service: PartidoService = Depends(get_partido_service)
):
    # Si no existe, service lanza RecursoNoEncontrado -> el handler
    # global la traduce a 404 automáticamente (ver exception_handlers.py)
    return service.obtener_por_id(partido_id)


@router.post("", response_model=PartidoResponse, status_code=201)
def crear_partido(
    datos: PartidoCreate, service: PartidoService = Depends(get_partido_service)
):
    return service.crear(nombre=datos.nombre)


@router.put("/{partido_id}", response_model=PartidoResponse)
def actualizar_partido(
    partido_id: int,
    datos: PartidoUpdate,
    service: PartidoService = Depends(get_partido_service),
):
    return service.actualizar(partido_id, nombre=datos.nombre)


@router.delete("/{partido_id}", status_code=200)
def eliminar_partido(
    partido_id: int, service: PartidoService = Depends(get_partido_service)
):
    service.eliminar(partido_id)
    return {"mensaje": "Partido eliminado correctamente"}


@router.patch("/{partido_id}/logo", response_model=PartidoResponse)
async def actualizar_logo(
    partido_id: int,
    archivo: UploadFile = File(...),
    service: PartidoService = Depends(get_partido_service),
):
    """
    Endpoint adicional (no parte del CRUD básico) para asociar un logo
    a un partido ya existente. Ver decisión de diseño: el logo es
    opcional al crear el partido, se puede agregar después.
    """
    from app.exceptions.dominio_exceptions import ValidacionFallida

    extension = os.path.splitext(archivo.filename)[1].lower()
    if extension not in EXTENSIONES_PERMITIDAS:
        raise ValidacionFallida(
            f"Formato de archivo no permitido: {extension}. "
            f"Formatos válidos: {', '.join(EXTENSIONES_PERMITIDAS)}"
        )

    # Verifica que el partido exista ANTES de escribir el archivo en disco
    service.obtener_por_id(partido_id)

    os.makedirs(LOGOS_DIR, exist_ok=True)
    nombre_archivo = f"{uuid.uuid4().hex}{extension}"
    ruta_completa = os.path.join(LOGOS_DIR, nombre_archivo)

    contenido = await archivo.read()
    with open(ruta_completa, "wb") as f:
        f.write(contenido)

    logo_url = f"/static/logos/{nombre_archivo}"
    return service.actualizar_logo(partido_id, logo_url=logo_url)
