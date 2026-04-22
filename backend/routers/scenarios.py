import json
from pathlib import Path
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/scenarios", tags=["scenarios"])

SCENARIOS_DIR = Path(__file__).parent.parent / "data" / "scenarios"


@router.get("/")
async def list_scenarios(lang: str = "fr"):
    """List available scenarios for a given language."""
    lang_dir = SCENARIOS_DIR / lang
    if not lang_dir.exists():
        raise HTTPException(status_code=404, detail=f"No scenarios for language: {lang}")
    scenarios = []
    for f in sorted(lang_dir.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        scenarios.append({
            "id": f.stem,
            "title": data.get("title", f.stem),
            "difficulty": data.get("difficulty", "intermediate"),
            "lang": lang,
        })
    return {"lang": lang, "scenarios": scenarios}


@router.get("/{lang}/{scenario_id}")
async def get_scenario(lang: str, scenario_id: str):
    """Return full scenario JSON."""
    path = SCENARIOS_DIR / lang / f"{scenario_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Scenario not found: {scenario_id}")
    return json.loads(path.read_text(encoding="utf-8"))
