import { useState } from "react";
import { votantesApi, ErrorApi } from "../services/api";

/**
 * Primer paso del flujo de votación: verificar/registrar la cédula.
 *
 * Nota de diseño: este componente NUNCA almacena la cédula en un
 * estado global ni la pasa "hacia arriba" más de lo necesario. Una
 * vez verificada, se entrega al padre solo para el siguiente paso
 * inmediato (emitir el voto) — reflejando en el frontend la misma
 * idea de no persistir vínculos innecesarios entre identidad y voto.
 */
function VerificacionCedula({ onVerificada }) {
  const [cedula, setCedula] = useState("");
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  async function manejarEnvio(evento) {
    evento.preventDefault();
    setError(null);

    if (!cedula.trim()) {
      setError("Ingresa tu número de cédula para continuar.");
      return;
    }

    setCargando(true);
    try {
      const respuesta = await votantesApi.verificar(cedula.trim());
      if (respuesta.puede_votar) {
        onVerificada(cedula.trim());
      } else {
        setError(respuesta.mensaje);
      }
    } catch (err) {
      if (err instanceof ErrorApi) {
        setError(err.message);
      } else {
        setError("No se pudo conectar con el servidor. Intenta de nuevo.");
      }
    } finally {
      setCargando(false);
    }
  }

  return (
    <div>
      <p style={{ color: "var(--color-tinta-suave)", marginBottom: "var(--espacio-md)" }}>
        Ingresa tu número de cédula para habilitar tu voto. Esta información
        solo se usa para verificar que aún no has votado.
      </p>

      <form onSubmit={manejarEnvio}>
        <div className="campo">
          <label htmlFor="cedula">Número de cédula</label>
          <input
            id="cedula"
            type="text"
            inputMode="numeric"
            value={cedula}
            onChange={(e) => setCedula(e.target.value)}
            placeholder="Ej. 1000000001"
            autoFocus
          />
        </div>

        {error && <div className="mensaje-error">{error}</div>}

        <button type="submit" className="boton boton-primario" disabled={cargando}>
          {cargando ? "Verificando..." : "Continuar"}
        </button>
      </form>
    </div>
  );
}

export default VerificacionCedula;
