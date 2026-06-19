import { BrowserRouter, Routes, Route } from "react-router-dom";
import Cabecera from "./components/Cabecera";
import VotarPage from "./pages/VotarPage";
import PartidosPage from "./pages/PartidosPage";
import CandidatosPage from "./pages/CandidatosPage";
import ResultadosPage from "./pages/ResultadosPage";
import "./styles/global.css";

function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Cabecera />
        <main className="contenido-principal">
          <Routes>
            <Route path="/" element={<VotarPage />} />
            <Route path="/partidos" element={<PartidosPage />} />
            <Route path="/candidatos" element={<CandidatosPage />} />
            <Route path="/resultados" element={<ResultadosPage />} />
          </Routes>
        </main>
        <footer className="pie-pagina">
          Sistema Electoral · Proyecto académico
        </footer>
      </div>
    </BrowserRouter>
  );
}

export default App;
