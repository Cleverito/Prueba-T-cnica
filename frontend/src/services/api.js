/**
 * Servicio centralizado de comunicación con la API.
 *
 * Toda llamada HTTP del frontend pasa por aquí — ningún componente
 * hace fetch() directamente. Esto refleja en el frontend el mismo
 * principio aplicado al backend con los Repositories: una sola capa
 * que sabe "cómo" comunicarse, separada de los componentes que solo
 * necesitan saber "qué" pedir.
 */

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

class ErrorApi extends Error {
  constructor(codigo, mensaje, detalles, status) {
    super(mensaje);
    this.codigo = codigo;
    this.detalles = detalles;
    this.status = status;
  }
}

async function manejarRespuesta(response) {
  if (response.status === 204) return null;

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    // Formato de error del backend: { error: { codigo, mensaje, detalles } }
    if (data?.error) {
      throw new ErrorApi(
        data.error.codigo,
        data.error.mensaje,
        data.error.detalles,
        response.status
      );
    }
    // Errores 422 de validación de Pydantic tienen otro formato
    throw new ErrorApi(
      "ERROR_DESCONOCIDO",
      data?.detail?.[0]?.msg || "Ocurrió un error inesperado",
      data,
      response.status
    );
  }

  return data;
}

async function solicitar(metodo, ruta, body) {
  const opciones = {
    method: metodo,
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  };
  const response = await fetch(`${API_URL}${ruta}`, opciones);
  return manejarRespuesta(response);
}

// ── Partidos ──
export const partidosApi = {
  listar: () => solicitar("GET", "/partidos"),
  obtener: (id) => solicitar("GET", `/partidos/${id}`),
  crear: (nombre) => solicitar("POST", "/partidos", { nombre }),
  actualizar: (id, nombre) => solicitar("PUT", `/partidos/${id}`, { nombre }),
  eliminar: (id) => solicitar("DELETE", `/partidos/${id}`),
};

// ── Candidatos ──
export const candidatosApi = {
  listar: () => solicitar("GET", "/candidatos"),
  obtener: (id) => solicitar("GET", `/candidatos/${id}`),
  crear: (nombre, numero, partido_id) =>
    solicitar("POST", "/candidatos", { nombre, numero, partido_id }),
  actualizar: (id, nombre, numero, partido_id) =>
    solicitar("PUT", `/candidatos/${id}`, { nombre, numero, partido_id }),
  eliminar: (id) => solicitar("DELETE", `/candidatos/${id}`),
};

// ── Votantes ──
export const votantesApi = {
  verificar: (cedula) => solicitar("POST", "/votantes/verificar", { cedula }),
};

// ── Votos ──
export const votosApi = {
  listar: () => solicitar("GET", "/votos"),
  registrar: (cedula, { candidatoId, partidoId }) => {
    const body = candidatoId
      ? { candidato_id: candidatoId }
      : { partido_id: partidoId };
    return solicitar("POST", `/votos?cedula=${encodeURIComponent(cedula)}`, body);
  },
};

// ── Resultados ──
export const resultadosApi = {
  obtener: () => solicitar("GET", "/resultados"),
};

export { ErrorApi };
