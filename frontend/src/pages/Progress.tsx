import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ProgressBar } from "../components/ProgressBar";

interface SessionRecord {
  scenario_id: string;
  lang: string;
  steps_completed: number;
  total_steps: number;
}

const SCENARIO_LABELS: Record<string, string> = {
  prefecture: "Préfecture",
  medecin: "Médecin généraliste",
  inscription_scolaire: "Inscription scolaire",
  entretien_embauche: "Entretien d'embauche",
  pharmacie: "Pharmacie",
  logement: "Logement",
};

export function Progress() {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<SessionRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/progress/")
      .then((r) => r.json())
      .then((data) => setSessions(data.sessions ?? []))
      .catch(() => setSessions([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-10">
      <div className="max-w-lg mx-auto">
        <div className="flex items-center gap-3 mb-8">
          <button onClick={() => navigate("/")} className="text-blue-700 text-sm hover:underline">
            ← Accueil
          </button>
          <h1 className="text-xl font-bold text-blue-800">Ma progression</h1>
        </div>

        {loading && (
          <p className="text-center text-gray-400 text-sm py-10">Chargement…</p>
        )}

        {!loading && sessions.length === 0 && (
          <div className="bg-white rounded-2xl p-8 shadow-sm text-center">
            <p className="text-gray-500 text-sm">
              Aucune session enregistrée. Commencez un scénario !
            </p>
            <button
              onClick={() => navigate("/")}
              className="mt-4 bg-blue-600 text-white px-5 py-2 rounded-xl text-sm hover:bg-blue-700"
            >
              Choisir un scénario
            </button>
          </div>
        )}

        <div className="space-y-4">
          {sessions.map((s) => (
            <div
              key={`${s.lang}-${s.scenario_id}`}
              className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100"
            >
              <div className="flex items-center justify-between mb-3">
                <p className="font-semibold text-gray-800">
                  {SCENARIO_LABELS[s.scenario_id] ?? s.scenario_id}
                </p>
                <button
                  onClick={() => navigate(`/chat/${s.lang}/${s.scenario_id}`)}
                  className="text-xs text-blue-600 hover:underline"
                >
                  Continuer →
                </button>
              </div>
              <ProgressBar
                current={s.steps_completed}
                total={s.total_steps}
                label={`${s.steps_completed}/${s.total_steps} étapes`}
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
