"""
Excepciones de dominio del sistema electoral.

Importante: estas clases NO saben nada de HTTP ni de FastAPI.
Una excepción de dominio describe un problema en el lenguaje del negocio
("el partido no existe", "la cédula ya votó"), no en el lenguaje del
protocolo de transporte ("404", "403"). La traducción a códigos HTTP
ocurre en exception_handlers.py, en un solo lugar.

Esto es una aplicación directa de Single Responsibility: los Services
lanzan estas excepciones sin preocuparse de qué status code les
corresponde; ese conocimiento vive exclusivamente en los handlers.
"""


class ErrorDominio(Exception):
    """Clase base de toda excepción de dominio del sistema electoral."""

    codigo: str = "ERROR_DOMINIO"

    def __init__(self, mensaje: str, detalles: dict | None = None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.detalles = detalles or {}


class RecursoNoEncontrado(ErrorDominio):
    """Se solicitó un recurso (por id) que no existe. → HTTP 404."""
    codigo = "RECURSO_NO_ENCONTRADO"

    def __init__(self, recurso: str, identificador):
        super().__init__(
            mensaje=f"{recurso} con id {identificador} no existe",
            detalles={"recurso": recurso, "id_solicitado": identificador},
        )


class RecursoDuplicado(ErrorDominio):
    """Se intentó crear algo que viola una restricción de unicidad. → HTTP 409."""
    codigo = "RECURSO_DUPLICADO"

    def __init__(self, recurso: str, campo: str, valor):
        super().__init__(
            mensaje=f"Ya existe {recurso} con {campo} = {valor!r}",
            detalles={"recurso": recurso, "campo": campo, "valor": valor},
        )


class ValidacionFallida(ErrorDominio):
    """Los datos de entrada no cumplen una regla de negocio. → HTTP 400."""
    codigo = "VALIDACION_FALLIDA"

    def __init__(self, mensaje: str, detalles: dict | None = None):
        super().__init__(mensaje=mensaje, detalles=detalles)


class OperacionNoPermitida(ErrorDominio):
    """
    Se intentó una operación que el estado actual de los datos no permite
    (ej. borrar un partido con candidatos asociados). → HTTP 409.
    """
    codigo = "OPERACION_NO_PERMITIDA"

    def __init__(self, mensaje: str, detalles: dict | None = None):
        super().__init__(mensaje=mensaje, detalles=detalles)


class VotanteNoHabilitado(ErrorDominio):
    """
    La cédula ya votó o está bloqueada por expiración de tiempo. → HTTP 403.
    Nunca debe incluir en 'detalles' información que permita inferir
    el voto específico de la cédula (eso violaría el secreto del voto).
    """
    codigo = "VOTANTE_NO_HABILITADO"

    def __init__(self, mensaje: str):
        super().__init__(mensaje=mensaje, detalles={})
