import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ChatWindow } from "../components/ChatWindow";

interface ScenarioData {
  title: string;
  system_prompt: string;
}

export function Chat() {
  const { lang, scenarioId } = useParams<{ lang: string; scenarioId: string }>();
  const navigate = useNavigate();
  const [scenario, setScenario] = useState<ScenarioData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!lang || !scenarioId) return;
    fetch(`/scenarios/${lang}/${scenarioId}`)
      .then((r) => r.json())
      .then((data) => setScenario(data))
      .catch(() => setError("Scénario introuvable."));
  }, [lang, scenarioId]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 mb-4">{error}</p>
          <button onClick={() => navigate("/")} className="text-blue-600 underline text-sm">
            Retour à l'accueil
          </button>
        </div>
      </div>
    );
  }

  if (!scenario) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-400 text-sm">
        Chargement du scénario…
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col">
      <div className="flex items-center gap-3 px-4 py-3">
        <button
          onClick={() => navigate("/")}
          className="text-blue-700 text-sm hover:underline"
        >
          ← Accueil
        </button>
      </div>
      <div className="flex-1 px-4 pb-6 max-w-2xl mx-auto w-full">
        <ChatWindow
          systemPrompt={scenario.system_prompt}
          scenarioTitle={scenario.title}
        />
      </div>
    </div>
  );
}
