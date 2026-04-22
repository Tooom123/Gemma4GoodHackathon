import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { ScenarioCard } from "../components/ScenarioCard";

interface Scenario {
  id: string;
  title: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  lang: string;
}

const LANGUAGES = [
  { code: "fr", label: "Français" },
  { code: "en", label: "English" },
  { code: "ar", label: "العربية" },
  { code: "es", label: "Español" },
];

export function Home() {
  const [lang, setLang] = useState("fr");
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch(`/scenarios/?lang=${lang}`)
      .then((r) => r.json())
      .then((data) => setScenarios(data.scenarios ?? []))
      .catch(() => setError("Impossible de charger les scénarios."))
      .finally(() => setLoading(false));
  }, [lang]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-10">
      <div className="max-w-lg mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-blue-800">LangBridge</h1>
          <p className="text-gray-600 mt-2 text-sm">
            Simulez des situations réelles pour apprendre la langue locale
          </p>
        </div>

        {/* Language selector */}
        <div className="flex gap-2 justify-center mb-6 flex-wrap">
          {LANGUAGES.map((l) => (
            <button
              key={l.code}
              onClick={() => setLang(l.code)}
              className={`px-4 py-1.5 rounded-full text-sm font-medium border transition-all ${
                lang === l.code
                  ? "bg-blue-600 text-white border-blue-600"
                  : "bg-white text-gray-700 border-gray-300 hover:border-blue-400"
              }`}
            >
              {l.label}
            </button>
          ))}
        </div>

        {/* Scenarios */}
        <div className="space-y-3">
          {loading && (
            <p className="text-center text-gray-500 text-sm py-8">Chargement…</p>
          )}
          {error && (
            <p className="text-center text-red-500 text-sm py-8">{error}</p>
          )}
          {!loading && !error && scenarios.length === 0 && (
            <p className="text-center text-gray-400 text-sm py-8">
              Aucun scénario disponible pour cette langue.
            </p>
          )}
          {scenarios.map((s) => (
            <ScenarioCard
              key={s.id}
              scenario={s}
              onSelect={(sc) => navigate(`/chat/${sc.lang}/${sc.id}`)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
