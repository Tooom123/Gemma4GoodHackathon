import { useState } from "react";
import type { PedagogyBlock } from "../utils/pedagogy";

interface Props {
  pedagogy: PedagogyBlock;
}

export function FeedbackPanel({ pedagogy }: Props) {
  const [open, setOpen] = useState(true);
  const hasCorrections = (pedagogy.corrections?.length ?? 0) > 0;
  const hasVocab = (pedagogy.vocabulary?.length ?? 0) > 0;

  if (!hasCorrections && !hasVocab && !pedagogy.encouragement) return null;

  return (
    <div className="mt-2 rounded-xl border border-blue-100 bg-blue-50 text-sm overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-3 py-2 text-blue-700 font-medium hover:bg-blue-100 transition-colors"
      >
        <span>📚 Feedback pédagogique</span>
        <span className="text-xs">{open ? "▲" : "▼"}</span>
      </button>

      {open && (
        <div className="px-3 pb-3 space-y-3">
          {pedagogy.encouragement && (
            <p className="text-green-700 font-medium">✓ {pedagogy.encouragement}</p>
          )}

          {hasCorrections && (
            <div>
              <p className="text-xs uppercase tracking-wide text-gray-500 mb-1">Corrections</p>
              <ul className="space-y-2">
                {pedagogy.corrections.map((c, i) => (
                  <li key={i} className="bg-white rounded-lg px-3 py-2 border border-red-100">
                    <p className="text-red-600 line-through text-xs">{c.original}</p>
                    <p className="text-green-700 font-medium">{c.corrected}</p>
                    {c.explanation && (
                      <p className="text-gray-500 text-xs mt-0.5">{c.explanation}</p>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {hasVocab && (
            <div>
              <p className="text-xs uppercase tracking-wide text-gray-500 mb-1">Vocabulaire</p>
              <ul className="space-y-1">
                {pedagogy.vocabulary.map((v, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="font-semibold text-blue-800 whitespace-nowrap">{v.word}</span>
                    <span className="text-gray-600">{v.definition}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
