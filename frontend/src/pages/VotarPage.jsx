import { useState } from "react";
import VerificacionCedula from "../components/VerificacionCedula";
import FormularioVoto from "../components/FormularioVoto";

function VotarPage() {
  const [cedula, setCedula] = useState(null);
  const [votoConfirmado, setVotoConfirmado] = useState(null);

  if (votoConfirmado) {
    return (
      <div>
        <h2 style={{ marginBottom: "var(--espacio-md)" }}>Voto registrado</h2>
        <div className="mensaje-exito">
          Tu voto quedó sellado correctamente. Gracias por participar.
        </div>
        <p style={{ fontFamily: "var(--fuente-mono)", fontSize: "0.8rem", color: "var(--color-tinta-suave)" }}>
          Registrado a las{" "}
          {new Date(votoConfirmado.hora_voto).toLocaleTimeString("es-CO")}
        </p>
      </div>
    );
  }

  if (!cedula) {
    return (
      <div>
        <h2 style={{ marginBottom: "var(--espacio-md)" }}>Verificación de identidad</h2>
        <VerificacionCedula onVerificada={setCedula} />
      </div>
    );
  }

  return (
    <div>
      <h2 style={{ marginBottom: "var(--espacio-md)" }}>Tarjetón electoral</h2>
      <FormularioVoto cedula={cedula} onVotoRegistrado={setVotoConfirmado} />
    </div>
  );
}

export default VotarPage;
