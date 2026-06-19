import { NavLink } from "react-router-dom";

function Cabecera() {
  return (
    <header className="cabecera">
      <div className="cabecera-contenido">
        <div>
          <div className="cabecera-eyebrow">República · Jornada Electoral</div>
          <h1 className="cabecera-titulo">Sistema Electoral</h1>
        </div>
        <nav className="navegacion">
          <NavLink to="/" end className={({ isActive }) => (isActive ? "activo" : "")}>
            Votar
          </NavLink>
          <NavLink to="/partidos" className={({ isActive }) => (isActive ? "activo" : "")}>
            Partidos
          </NavLink>
          <NavLink to="/candidatos" className={({ isActive }) => (isActive ? "activo" : "")}>
            Candidatos
          </NavLink>
          <NavLink to="/resultados" className={({ isActive }) => (isActive ? "activo" : "")}>
            Resultados
          </NavLink>
        </nav>
      </div>
    </header>
  );
}

export default Cabecera;
