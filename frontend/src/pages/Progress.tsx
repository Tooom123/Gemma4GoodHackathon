import { useNavigate } from "react-router-dom";
import { ProgressBar } from "../components/ProgressBar";

// Placeholder data — will be replaced by SQLite backend in week 3
const MOCK_PROGRESS = [
  { id: "prefecture", title: "Préfecture", steps: 3, total: 5 },
  { id: "medecin", title: "Médecin", steps: 1, total: 5 },
  { id: "inscription_scolaire", title: "Inscription scolaire", steps: 0, total: 5 },
];

export function Progress() {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-10">
      <div className="max-w-lg mx-auto">
        <div className="flex items-center gap-3 mb-8">
          <button onClick={() => navigate("/")} className="text-blue-700 text-sm hover:underline">
            ← Accueil
          </button>
          <h1 className="text-xl font-bold text-blue-800">Ma progression</h1>
        </div>
        <div className="space-y-4">
          {MOCK_PROGRESS.map((s) => (
            <div key={s.id} className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
              <p className="font-semibold text-gray-800 mb-3">{s.title}</p>
              <ProgressBar current={s.steps} total={s.total} label={`${s.steps}/${s.total} étapes`} />
            </div>
          ))}
        </div>
        <p className="text-center text-xs text-gray-400 mt-6">
          Suivi SQLite complet disponible en semaine 3
        </p>
      </div>
    </div>
  );
}
