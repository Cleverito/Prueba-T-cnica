"""
Traducción centralizada de excepciones de dominio a respuestas HTTP.

Este es el ÚNICO lugar del proyecto que sabe qué status code HTTP
corresponde a cada excepción de dominio. Si en el futuro se cambia
de FastAPI a otro framework, solo este archivo necesita reescribirse;
los Services y Repositories permanecen intactos.

Formato de respuesta de error (consistente en todo el sistema):
{
  "error": {
    "codigo": "RECURSO_NO_ENCONTRADO",
    "mensaje": "El partido con id 7 no existe",
    "detalles": { "recurso": "Partido", "id_solicitado": 7 }
  }
}
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.dominio_exceptions import (
    ErrorDominio,
    RecursoNoEncontrado,
    RecursoDuplicado,
    ValidacionFallida,
    OperacionNoPermitida,
    VotanteNoHabilitado,
)

logger = logging.getLogger("sistema_electoral")

# Mapeo explícito: tipo de excepción de dominio -> status code HTTP.
# Mantenerlo como diccionario (en vez de if/elif repetidos) hace trivial
# agregar una nueva excepción de dominio en el futuro: solo se añade
# una línea aquí, sin tocar el resto de la lógica del handler.
_MAPEO_STATUS_CODE = {
    RecursoNoEncontrado: 404,
    RecursoDuplicado: 409,
    ValidacionFallida: 400,
    OperacionNoPermitida: 409,
    VotanteNoHabilitado: 403,
}


def _construir_respuesta_error(codigo: str, mensaje: str, detalles: dict) -> dict:
    return {
        "error": {
            "codigo": codigo,
            "mensaje": mensaje,
            "detalles": detalles,
        }
    }


def registrar_handlers(app: FastAPI) -> None:
    """
    Registra en la aplicación FastAPI los manejadores de excepciones.
    Se llama una sola vez desde main.py al iniciar la aplicación.
    """

    @app.exception_handler(ErrorDominio)
    async def manejar_error_dominio(request: Request, exc: ErrorDominio):
        status_code = _MAPEO_STATUS_CODE.get(type(exc), 400)
        return JSONResponse(
            status_code=status_code,
            content=_construir_respuesta_error(exc.codigo, exc.mensaje, exc.detalles),
        )

    @app.exception_handler(Exception)
    async def manejar_error_inesperado(request: Request, exc: Exception):
        # Cualquier excepción NO anticipada (fallo de red, BD caída, bug no
        # contemplado). Se registra el detalle real en logs del servidor,
        # pero NUNCA se expone ese detalle interno al cliente: filtrar
        # trazas de error al exterior es un riesgo de seguridad.
        logger.exception("Error interno no controlado")
        return JSONResponse(
            status_code=500,
            content=_construir_respuesta_error(
                codigo="ERROR_INTERNO",
                mensaje="Ocurrió un error interno. Intenta de nuevo más tarde.",
                detalles={},
            ),
        )
