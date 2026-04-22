import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Home } from "./pages/Home";
import { Chat } from "./pages/Chat";
import { Progress } from "./pages/Progress";
import { useOnlineStatus } from "./hooks/useOnlineStatus";

function OfflineBanner() {
  const isOnline = useOnlineStatus();
  if (isOnline) return null;
  return (
    <div className="fixed top-0 inset-x-0 z-50 bg-amber-500 text-white text-center text-xs py-1 font-medium">
      Mode hors-ligne — Ollama fonctionne localement, aucune donnée n'est envoyée
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <OfflineBanner />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/chat/:lang/:scenarioId" element={<Chat />} />
        <Route path="/progress" element={<Progress />} />
      </Routes>
    </BrowserRouter>
  );
}
