import { useState, useEffect } from "react";
import { candidatosApi, partidosApi, ErrorApi } from "../services/api";

function CandidatosPage() {
  const [candidatos, setCandidatos] = useState([]);
  const [partidos, setPartidos] = useState([]);
  const [nombreNuevo, setNombreNuevo] = useState("");
  const [numeroNuevo, setNumeroNuevo] = useState("");
  const [partidoNuevoId, setPartidoNuevoId] = useState("");
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  function cargarDatos() {
    setCargando(true);
    Promise.all([candidatosApi.listar(), partidosApi.listar()])
      .then(([listaCandidatos, listaPartidos]) => {
        setCandidatos(listaCandidatos);
        setPartidos(listaPartidos);
      })
      .catch(() => setError("No se pudieron cargar los datos."))
      .finally(() => setCargando(false));
  }

  useEffect(cargarDatos, []);

  async function crearCandidato(evento) {
    evento.preventDefault();
    setError(null);

    if (!nombreNuevo.trim() || !numeroNuevo.trim() || !partidoNuevoId) {
      setError("Completa nombre, número y partido para registrar el candidato.");
      return;
    }

    try {
      await candidatosApi.crear(nombreNuevo.trim(), numeroNuevo.trim(), Number(partidoNuevoId));
      setNombreNuevo("");
      setNumeroNuevo("");
      setPartidoNuevoId("");
      cargarDatos();
    } catch (err) {
      setError(err instanceof ErrorApi ? err.message : "No se pudo crear el candidato.");
    }
  }

  async function eliminarCandidato(id) {
    setError(null);
    try {
      await candidatosApi.eliminar(id);
      cargarDatos();
    } catch (err) {
      setError(err instanceof ErrorApi ? err.message : "No se pudo eliminar el candidato.");
    }
  }

  if (cargando) return <p className="cargando">Cargando candidatos...</p>;

  return (
    <div>
      <h2 style={{ marginBottom: "var(--espacio-md)" }}>Candidatos</h2>

      {error && <div className="mensaje-error">{error}</div>}

      {partidos.length === 0 ? (
        <p style={{ color: "var(--color-tinta-suave)" }}>
          Registra primero al menos un partido antes de agregar candidatos.
        </p>
      ) : (
        <form
          onSubmit={crearCandidato}
          style={{ display: "flex", gap: "var(--espacio-sm)", marginBottom: "var(--espacio-lg)", flexWrap: "wrap" }}
        >
          <input
            type="text"
            value={nombreNuevo}
            onChange={(e) => setNombreNuevo(e.target.value)}
            placeholder="Nombre del candidato"
            style={{ flex: 2, minWidth: "180px", padding: "0.65rem 0.8rem", border: "1.5px solid var(--color-linea)", borderRadius: "2px" }}
          />
          <input
            type="text"
            value={numeroNuevo}
            onChange={(e) => setNumeroNuevo(e.target.value)}
            placeholder="Número (ej. 01A)"
            style={{ flex: 1, minWidth: "100px", padding: "0.65rem 0.8rem", border: "1.5px solid var(--color-linea)", borderRadius: "2px", fontFamily: "var(--fuente-mono)" }}
          />
          <select
            value={partidoNuevoId}
            onChange={(e) => setPartidoNuevoId(e.target.value)}
            style={{ flex: 1, minWidth: "160px", padding: "0.65rem 0.8rem", border: "1.5px solid var(--color-linea)", borderRadius: "2px" }}
          >
            <option value="">Selecciona partido</option>
            {partidos.map((p) => (
              <option key={p.id} value={p.id}>
                {p.nombre}
              </option>
            ))}
          </select>
          <button type="submit" className="boton boton-primario">
            Registrar candidato
          </button>
        </form>
      )}

      {candidatos.length === 0 ? (
        <p style={{ color: "var(--color-tinta-suave)" }}>Aún no hay candidatos registrados.</p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "2px solid var(--color-tinta)" }}>
              <th style={{ textAlign: "left", padding: "0.5rem", fontFamily: "var(--fuente-mono)", fontSize: "0.75rem", textTransform: "uppercase" }}>Número</th>
              <th style={{ textAlign: "left", padding: "0.5rem", fontFamily: "var(--fuente-mono)", fontSize: "0.75rem", textTransform: "uppercase" }}>Nombre</th>
              <th style={{ textAlign: "left", padding: "0.5rem", fontFamily: "var(--fuente-mono)", fontSize: "0.75rem", textTransform: "uppercase" }}>Partido</th>
              <th style={{ width: "100px" }}></th>
            </tr>
          </thead>
          <tbody>
            {candidatos.map((candidato) => (
              <tr key={candidato.id} style={{ borderBottom: "1px solid var(--color-linea)" }}>
                <td style={{ padding: "0.6rem 0.5rem", fontFamily: "var(--fuente-mono)" }}>{candidato.numero}</td>
                <td style={{ padding: "0.6rem 0.5rem" }}>{candidato.nombre}</td>
                <td style={{ padding: "0.6rem 0.5rem" }}>{candidato.partido.nombre}</td>
                <td style={{ padding: "0.6rem 0.5rem", textAlign: "right" }}>
                  <button
                    className="boton"
                    onClick={() => eliminarCandidato(candidato.id)}
                    style={{ padding: "0.3rem 0.7rem", fontSize: "0.8rem" }}
                  >
                    Eliminar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default CandidatosPage;
