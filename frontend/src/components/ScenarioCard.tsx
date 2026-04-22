interface Scenario {
  id: string;
  title: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  lang: string;
}

interface Props {
  scenario: Scenario;
  onSelect: (scenario: Scenario) => void;
}

const difficultyLabel: Record<string, string> = {
  beginner: "Débutant",
  intermediate: "Intermédiaire",
  advanced: "Avancé",
};

const difficultyColor: Record<string, string> = {
  beginner: "bg-green-100 text-green-700",
  intermediate: "bg-yellow-100 text-yellow-700",
  advanced: "bg-red-100 text-red-700",
};

export function ScenarioCard({ scenario, onSelect }: Props) {
  return (
    <button
      onClick={() => onSelect(scenario)}
      className="w-full text-left rounded-2xl border border-gray-200 p-5 hover:border-blue-400 hover:shadow-md transition-all bg-white"
    >
      <div className="flex items-start justify-between gap-3">
        <h3 className="font-semibold text-gray-900 text-sm">{scenario.title}</h3>
        <span
          className={`shrink-0 text-xs px-2 py-0.5 rounded-full font-medium ${
            difficultyColor[scenario.difficulty] ?? "bg-gray-100 text-gray-600"
          }`}
        >
          {difficultyLabel[scenario.difficulty] ?? scenario.difficulty}
        </span>
      </div>
    </button>
  );
}
