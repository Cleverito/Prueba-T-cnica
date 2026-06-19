# Especificación de la API

API REST construida con FastAPI. La documentación interactiva (Swagger UI) está siempre disponible en `/docs` mientras el servidor está corriendo, generada automáticamente a partir de los schemas Pydantic.

## Formato de respuesta de error

Toda respuesta de error de la API sigue el mismo formato, sin excepción:

```json
{
  "error": {
    "codigo": "RECURSO_NO_ENCONTRADO",
    "mensaje": "El partido con id 7 no existe",
    "detalles": {
      "recurso": "Partido",
      "id_solicitado": 7
    }
  }
}
```

| Campo | Propósito |
|---|---|
| `codigo` | Constante estable, pensada para uso programático en el frontend (no cambia entre redacciones) |
| `mensaje` | Texto legible para mostrar al usuario |
| `detalles` | Contexto adicional específico del caso (puede ser un objeto vacío) |

## Catálogo de códigos de error

| Código | Status HTTP | Cuándo ocurre |
|---|---|---|
| `RECURSO_NO_ENCONTRADO` | 404 | Se solicita un `id` que no existe |
| `RECURSO_DUPLICADO` | 409 | Se intenta crear algo que viola una restricción de unicidad |
| `VALIDACION_FALLIDA` | 400 | Los datos de entrada no cumplen una regla de negocio |
| `OPERACION_NO_PERMITIDA` | 409 | El estado actual de los datos no permite la operación (ej. borrar un partido con candidatos) |
| `VOTANTE_NO_HABILITADO` | 403 | La cédula ya votó, está bloqueada, o no fue verificada previamente |
| `ERROR_INTERNO` | 500 | Cualquier fallo no anticipado; nunca expone detalles internos al cliente |

Las validaciones de formato de Pydantic (ej. tipo de dato incorrecto, campo faltante) devuelven `422` con el formato propio de FastAPI, no el formato anterior — son errores de la capa de transporte, no del dominio.

## Partidos

| Método | Endpoint | Body | Status éxito | Errores posibles |
|---|---|---|---|---|
| GET | `/partidos` | — | 200 | — |
| GET | `/partidos/{id}` | — | 200 | 404 |
| POST | `/partidos` | `{ "nombre": string }` | 201 | 400, 409 |
| PUT | `/partidos/{id}` | `{ "nombre": string }` | 200 | 404, 400, 409 |
| DELETE | `/partidos/{id}` | — | 200 | 404, 409 (si tiene candidatos asociados) |
| PATCH | `/partidos/{id}/logo` | multipart/form-data (archivo) | 200 | 404, 400 (formato de archivo no soportado) |

## Candidatos

| Método | Endpoint | Body | Status éxito | Errores posibles |
|---|---|---|---|---|
| GET | `/candidatos` | — | 200 | — |
| GET | `/candidatos/{id}` | — | 200 | 404 |
| POST | `/candidatos` | `{ "nombre": string, "numero": string, "partido_id": int }` | 201 | 400, 404 (partido inexistente), 409 (numero duplicado en el partido) |
| PUT | `/candidatos/{id}` | igual que POST | 200 | 404, 400, 409 |
| DELETE | `/candidatos/{id}` | — | 200 | 404, 409 (si tiene votos asociados) |

La respuesta de `Candidato` incluye el objeto `Partido` completo anidado (no solo su `id`), para que el frontend pueda mostrar nombre y logo sin una llamada adicional.

## Votos

**Intencionalmente sin PUT ni DELETE**: un voto, una vez registrado, es inmutable. Ver `decisiones_diseno.md`.

| Método | Endpoint | Body / Query | Status éxito | Errores posibles |
|---|---|---|---|---|
| GET | `/votos` | — | 200 | — |
| GET | `/votos/{id}` | — | 200 | 404 |
| POST | `/votos?cedula=...` (opcional) | `{ "candidato_id": int }` **o** `{ "partido_id": int }` (nunca ambos, nunca ninguno) | 201 | 404 (candidato/partido inexistente), 403 (votante no habilitado, solo si se envió cedula), 422 (ambos o ningún campo enviado) |

El parámetro `cedula` es **opcional**. Sin él, el voto se registra cumpliendo únicamente el requisito base (candidato/partido + momento), sin ningún control de unicidad. Con él, se activa la verificación de votante (mejora sobre el enunciado base, ver `decisiones_diseno.md`): la cédula debe haber sido verificada previamente vía `/votantes/verificar`, no debe haber votado ya, y no debe estar expirada.

La `cedula`, cuando se envía, va como query parameter, no en el body, porque no forma parte del registro persistido del voto — solo se usa para validar y actualizar el estado del votante. Las respuestas de este endpoint nunca incluyen ningún dato relacionado a la cédula del votante.

## Votantes

| Método | Endpoint | Body | Status éxito | Respuesta |
|---|---|---|---|---|
| POST | `/votantes/verificar` | `{ "cedula": string }` | 200 | `{ "puede_votar": bool, "mensaje": string }` |

No existe ningún endpoint que liste votantes. Esta es una decisión de diseño deliberada, no una omisión: exponer el padrón completo de cédulas comprometería el secreto del voto.

## Resultados

| Método | Endpoint | Status éxito | Respuesta |
|---|---|---|---|
| GET | `/resultados` | 200 | Conteo agregado jerárquico (ver ejemplo abajo) |

```json
{
  "total_votos": 1500,
  "por_partido": [
    {
      "partido_id": 1,
      "partido_nombre": "Partido Verde",
      "votos_totales": 800,
      "votos_directos_partido": 50,
      "candidatos": [
        { "candidato_id": 3, "candidato_nombre": "Ana Pérez", "numero": "01A", "votos": 500 },
        { "candidato_id": 4, "candidato_nombre": "Luis Gómez", "numero": "02A", "votos": 250 }
      ]
    }
  ]
}
```

`votos_totales` por partido equivale a la suma de los votos de sus candidatos más `votos_directos_partido` (votos sin candidato específico). Este endpoint no corresponde a una tabla propia: se calcula mediante agregación SQL (`GROUP BY`/`COUNT`) sobre `votos`, `candidatos` y `partidos`.
