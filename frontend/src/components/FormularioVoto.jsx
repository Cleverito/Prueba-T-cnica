import { useState, useEffect } from "react";
import { candidatosApi, votosApi, ErrorApi } from "../services/api";

/**
 * Segundo paso del flujo de votación.
 *
 * Decisión de diseño relevante: la selección es de tipo radio (única),
 * nunca checkboxes. Esto hace que el "voto nulo por doble marcación"
 * sea estructuralmente imposible en esta interfaz — no se modela como
 * estado en la base de datos porque el frontend ya lo previene.
 */
function FormularioVoto({ cedula, onVotoRegistrado }) {
  const [candidatos, setCandidatos] = useState([]);
  const [seleccion, setSeleccion] = useState(null);
  const [cargandoCandidatos, setCargandoCandidatos] = useState(true);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState(null);
  const [confirmando, setConfirmando] = useState(false);

  useEffect(() => {
    candidatosApi
      .listar()
      .then(setCandidatos)
      .catch(() => setError("No se pudo cargar la lista de candidatos."))
      .finally(() => setCargandoCandidatos(false));
  }, []);

  const partidosConCandidatos = candidatos.reduce((acc, candidato) => {
    const partidoId = candidato.partido.id;
    if (!acc[partidoId]) {
      acc[partidoId] = { partido: candidato.partido, candidatos: [] };
    }
    acc[partidoId].candidatos.push(candidato);
    return acc;
  }, {});

  async function confirmarVoto() {
    if (!seleccion) return;
    setEnviando(true);
    setError(null);

    try {
      const voto = await votosApi.registrar(cedula, {
        candidatoId: seleccion.tipo === "candidato" ? seleccion.id : null,
        partidoId: seleccion.tipo === "partido" ? seleccion.id : null,
      });
      onVotoRegistrado(voto);
    } catch (err) {
      setConfirmando(false);
      if (err instanceof ErrorApi) {
        setError(err.message);
      } else {
        setError("No se pudo registrar el voto. Intenta de nuevo.");
      }
    } finally {
      setEnviando(false);
    }
  }

  if (cargandoCandidatos) {
    return <p className="cargando">Cargando tarjetón electoral...</p>;
  }

  return (
    <div>
      <p style={{ color: "var(--color-tinta-suave)", marginBottom: "var(--espacio-md)" }}>
        Selecciona un candidato, o vota directamente por un partido. Tu voto
        es anónimo: el sistema no guarda ninguna relación entre tu cédula y
        tu selección.
      </p>

      {error && <div className="mensaje-error">{error}</div>}

      {Object.values(partidosConCandidatos).map(({ partido, candidatos: lista }) => (
        <fieldset
          key={partido.id}
          style={{
            border: "1px solid var(--color-linea)",
            borderRadius: "2px",
            padding: "var(--espacio-md)",
            marginBottom: "var(--espacio-md)",
          }}
        >
          <legend style={{ fontFamily: "var(--fuente-display)", fontWeight: 600, padding: "0 0.5rem" }}>
            {partido.nombre}
          </legend>

          {lista.map((candidato) => (
            <label
              key={candidato.id}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.75rem",
                padding: "0.6rem 0",
                cursor: "pointer",
                borderBottom: "1px solid var(--color-linea)",
              }}
            >
              <input
                type="radio"
                name="seleccion-voto"
                checked={seleccion?.tipo === "candidato" && seleccion.id === candidato.id}
                onChange={() =>
                  setSeleccion({ tipo: "candidato", id: candidato.id, etiqueta: candidato.nombre })
                }
              />
              <span style={{ fontFamily: "var(--fuente-mono)", color: "var(--color-tinta-suave)" }}>
                {candidato.numero}
              </span>
              <span>{candidato.nombre}</span>
            </label>
          ))}

          <label style={{ display: "flex", alignItems: "center", gap: "0.75rem", padding: "0.6rem 0", cursor: "pointer" }}>
            <input
              type="radio"
              name="seleccion-voto"
              checked={seleccion?.tipo === "partido" && seleccion.id === partido.id}
              onChange={() =>
                setSeleccion({ tipo: "partido", id: partido.id, etiqueta: `Voto directo a ${partido.nombre}` })
              }
            />
            <span style={{ fontStyle: "italic", color: "var(--color-tinta-suave)" }}>
              Voto directo por el partido (sin candidato)
            </span>
          </label>
        </fieldset>
      ))}

      {!confirmando ? (
        <button className="boton boton-primario" disabled={!seleccion} onClick={() => setConfirmando(true)}>
          Continuar con mi selección
        </button>
      ) : (
        <div style={{ border: "2px solid var(--color-sello)", padding: "var(--espacio-md)", background: "rgba(139, 30, 30, 0.04)" }}>
          <p style={{ marginBottom: "var(--espacio-sm)" }}>
            Confirmas tu voto por: <strong>{seleccion.etiqueta}</strong>
          </p>
          <p style={{ fontFamily: "var(--fuente-mono)", fontSize: "0.8rem", color: "var(--color-tinta-suave)", marginBottom: "var(--espacio-md)" }}>
            Esta acción no se puede deshacer.
          </p>
          <div style={{ display: "flex", gap: "var(--espacio-sm)" }}>
            <button className="boton boton-primario" onClick={confirmarVoto} disabled={enviando}>
              {enviando ? "Registrando..." : "Sellar mi voto"}
            </button>
            <button className="boton" onClick={() => setConfirmando(false)} disabled={enviando}>
              Volver a elegir
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default FormularioVoto;
