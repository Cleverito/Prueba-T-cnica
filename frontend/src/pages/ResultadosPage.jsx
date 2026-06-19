import { useState, useEffect } from "react";
import { resultadosApi } from "../services/api";

function ResultadosPage() {
  const [resultados, setResultados] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    resultadosApi
      .obtener()
      .then(setResultados)
      .catch(() => setError("No se pudieron cargar los resultados."))
      .finally(() => setCargando(false));
  }, []);

  if (cargando) return <p className="cargando">Calculando resultados...</p>;
  if (error) return <div className="mensaje-error">{error}</div>;

  const maximoVotos = Math.max(
    1,
    ...resultados.por_partido.map((p) => p.votos_totales)
  );

  return (
    <div>
      <h2 style={{ marginBottom: "0.25rem" }}>Resultados</h2>
      <p style={{ fontFamily: "var(--fuente-mono)", fontSize: "0.85rem", color: "var(--color-tinta-suave)", marginBottom: "var(--espacio-lg)" }}>
        Total de votos escrutados: {resultados.total_votos}
      </p>

      {resultados.por_partido.length === 0 ? (
        <p style={{ color: "var(--color-tinta-suave)" }}>Aún no hay partidos registrados.</p>
      ) : (
        resultados.por_partido.map((partido) => (
          <div key={partido.partido_id} style={{ marginBottom: "var(--espacio-lg)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: "0.4rem" }}>
              <h3 style={{ fontSize: "1.1rem" }}>{partido.partido_nombre}</h3>
              <span style={{ fontFamily: "var(--fuente-mono)", fontWeight: 700 }}>
                {partido.votos_totales} voto{partido.votos_totales !== 1 ? "s" : ""}
              </span>
            </div>

            {/* Barra tipo "tira de resultados" */}
            <div style={{ height: "10px", background: "var(--color-papel-alt)", borderRadius: "2px", overflow: "hidden", marginBottom: "0.75rem" }}>
              <div
                style={{
                  height: "100%",
                  width: `${(partido.votos_totales / maximoVotos) * 100}%`,
                  background: "var(--color-sello)",
                  transition: "width 0.4s ease",
                }}
              />
            </div>

            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.9rem" }}>
              <tbody>
                {partido.candidatos.map((candidato) => (
                  <tr key={candidato.candidato_id} style={{ borderBottom: "1px solid var(--color-linea)" }}>
                    <td style={{ padding: "0.4rem 0.5rem", fontFamily: "var(--fuente-mono)", color: "var(--color-tinta-suave)", width: "60px" }}>
                      {candidato.numero}
                    </td>
                    <td style={{ padding: "0.4rem 0.5rem" }}>{candidato.candidato_nombre}</td>
                    <td style={{ padding: "0.4rem 0.5rem", textAlign: "right", fontFamily: "var(--fuente-mono)" }}>
                      {candidato.votos}
                    </td>
                  </tr>
                ))}
                {partido.votos_directos_partido > 0 && (
                  <tr style={{ borderBottom: "1px solid var(--color-linea)" }}>
                    <td colSpan={2} style={{ padding: "0.4rem 0.5rem", fontStyle: "italic", color: "var(--color-tinta-suave)" }}>
                      Voto directo al partido
                    </td>
                    <td style={{ padding: "0.4rem 0.5rem", textAlign: "right", fontFamily: "var(--fuente-mono)" }}>
                      {partido.votos_directos_partido}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        ))
      )}
    </div>
  );
}

export default ResultadosPage;
