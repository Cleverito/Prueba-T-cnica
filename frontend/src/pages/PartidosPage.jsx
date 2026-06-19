import { useState, useEffect } from "react";
import { partidosApi, ErrorApi } from "../services/api";

function PartidosPage() {
  const [partidos, setPartidos] = useState([]);
  const [nombreNuevo, setNombreNuevo] = useState("");
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);
  const [editandoId, setEditandoId] = useState(null);
  const [nombreEdicion, setNombreEdicion] = useState("");

  function cargarPartidos() {
    setCargando(true);
    partidosApi
      .listar()
      .then(setPartidos)
      .catch(() => setError("No se pudieron cargar los partidos."))
      .finally(() => setCargando(false));
  }

  useEffect(cargarPartidos, []);

  async function crearPartido(evento) {
    evento.preventDefault();
    setError(null);
    if (!nombreNuevo.trim()) return;

    try {
      await partidosApi.crear(nombreNuevo.trim());
      setNombreNuevo("");
      cargarPartidos();
    } catch (err) {
      setError(err instanceof ErrorApi ? err.message : "No se pudo crear el partido.");
    }
  }

  async function guardarEdicion(id) {
    setError(null);
    try {
      await partidosApi.actualizar(id, nombreEdicion.trim());
      setEditandoId(null);
      cargarPartidos();
    } catch (err) {
      setError(err instanceof ErrorApi ? err.message : "No se pudo actualizar el partido.");
    }
  }

  async function eliminarPartido(id) {
    setError(null);
    try {
      await partidosApi.eliminar(id);
      cargarPartidos();
    } catch (err) {
      setError(err instanceof ErrorApi ? err.message : "No se pudo eliminar el partido.");
    }
  }

  return (
    <div>
      <h2 style={{ marginBottom: "var(--espacio-md)" }}>Partidos políticos</h2>

      {error && <div className="mensaje-error">{error}</div>}

      <form onSubmit={crearPartido} style={{ display: "flex", gap: "var(--espacio-sm)", marginBottom: "var(--espacio-lg)" }}>
        <input
          type="text"
          value={nombreNuevo}
          onChange={(e) => setNombreNuevo(e.target.value)}
          placeholder="Nombre del nuevo partido"
          style={{
            flex: 1,
            padding: "0.65rem 0.8rem",
            border: "1.5px solid var(--color-linea)",
            borderRadius: "2px",
            fontFamily: "var(--fuente-cuerpo)",
            fontSize: "1rem",
          }}
        />
        <button type="submit" className="boton boton-primario">
          Registrar partido
        </button>
      </form>

      {cargando ? (
        <p className="cargando">Cargando partidos...</p>
      ) : partidos.length === 0 ? (
        <p style={{ color: "var(--color-tinta-suave)" }}>
          Aún no hay partidos registrados. Usa el formulario para crear el primero.
        </p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "2px solid var(--color-tinta)" }}>
              <th style={{ textAlign: "left", padding: "0.5rem", fontFamily: "var(--fuente-mono)", fontSize: "0.75rem", textTransform: "uppercase" }}>
                Nombre
              </th>
              <th style={{ width: "180px" }}></th>
            </tr>
          </thead>
          <tbody>
            {partidos.map((partido) => (
              <tr key={partido.id} style={{ borderBottom: "1px solid var(--color-linea)" }}>
                <td style={{ padding: "0.6rem 0.5rem" }}>
                  {editandoId === partido.id ? (
                    <input
                      type="text"
                      value={nombreEdicion}
                      onChange={(e) => setNombreEdicion(e.target.value)}
                      style={{ padding: "0.4rem", border: "1px solid var(--color-linea)", width: "100%" }}
                      autoFocus
                    />
                  ) : (
                    partido.nombre
                  )}
                </td>
                <td style={{ padding: "0.6rem 0.5rem", textAlign: "right", whiteSpace: "nowrap" }}>
                  {editandoId === partido.id ? (
                    <>
                      <button className="boton" onClick={() => guardarEdicion(partido.id)} style={{ marginRight: "0.4rem", padding: "0.3rem 0.7rem", fontSize: "0.8rem" }}>
                        Guardar
                      </button>
                      <button className="boton" onClick={() => setEditandoId(null)} style={{ padding: "0.3rem 0.7rem", fontSize: "0.8rem" }}>
                        Cancelar
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        className="boton"
                        onClick={() => {
                          setEditandoId(partido.id);
                          setNombreEdicion(partido.nombre);
                        }}
                        style={{ marginRight: "0.4rem", padding: "0.3rem 0.7rem", fontSize: "0.8rem" }}
                      >
                        Editar
                      </button>
                      <button
                        className="boton"
                        onClick={() => eliminarPartido(partido.id)}
                        style={{ padding: "0.3rem 0.7rem", fontSize: "0.8rem" }}
                      >
                        Eliminar
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default PartidosPage;
