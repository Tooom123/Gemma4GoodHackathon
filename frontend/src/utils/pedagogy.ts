export interface Correction {
  original: string;
  corrected: string;
  explanation: string;
}

export interface VocabEntry {
  word: string;
  definition: string;
}

export interface PedagogyBlock {
  corrections: Correction[];
  vocabulary: VocabEntry[];
  encouragement: string;
}

export interface ExtractResult {
  cleanText: string;
  pedagogy: PedagogyBlock | null;
}

/**
 * Split assistant text into clean conversational text + structured pedagogy block.
 * Gemma emits the JSON on a dedicated line after the main response.
 */
export function extractPedagogy(text: string): ExtractResult {
  const lines = text.split("\n");

  // Scan from bottom — find the first line that is a JSON object with "corrections"
  for (let i = lines.length - 1; i >= 0; i--) {
    const line = lines[i].trim();
    if (line.startsWith("{") && line.includes('"corrections"')) {
      try {
        const block = JSON.parse(line) as PedagogyBlock;
        const cleanLines = lines.filter((_, j) => j !== i);
        return { cleanText: cleanLines.join("\n").trim(), pedagogy: block };
      } catch {
        // not valid JSON, keep looking
      }
    }
  }

  return { cleanText: text, pedagogy: null };
}

export function hasFeedback(p: PedagogyBlock | null): boolean {
  if (!p) return false;
  return (
    (p.corrections?.length ?? 0) > 0 ||
    (p.vocabulary?.length ?? 0) > 0 ||
    !!p.encouragement
  );
}
