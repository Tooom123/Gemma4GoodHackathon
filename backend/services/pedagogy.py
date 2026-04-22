import json
import re

# Gemma outputs the feedback block as a single JSON line containing "corrections"
_JSON_LINE_RE = re.compile(r'(\{[^\n]*"corrections"[^\n]*\})', re.DOTALL)


def extract_pedagogy(text: str) -> tuple[str, dict | None]:
    """
    Split assistant response into (clean_text, pedagogy_dict | None).

    Gemma is instructed to emit a JSON object on a separate line:
      {"corrections": [...], "vocabulary": [...], "encouragement": "..."}

    We scan lines in reverse for the first parseable JSON object containing
    "corrections", strip it from the text, and return both parts.
    """
    lines = text.split("\n")
    for i in range(len(lines) - 1, -1, -1):
        stripped = lines[i].strip()
        if stripped.startswith("{") and "corrections" in stripped:
            try:
                block = json.loads(stripped)
                clean_lines = [l for j, l in enumerate(lines) if j != i]
                return "\n".join(clean_lines).strip(), block
            except json.JSONDecodeError:
                pass

    # Fallback: try multiline JSON via regex
    match = _JSON_LINE_RE.search(text)
    if match:
        try:
            block = json.loads(match.group(1))
            clean = text[: match.start()].rstrip() + text[match.end() :].lstrip()
            return clean.strip(), block
        except json.JSONDecodeError:
            pass

    return text, None
