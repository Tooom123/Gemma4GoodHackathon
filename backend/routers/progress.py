from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, update
from backend.models.database import SessionLocal, SessionRecord

router = APIRouter(prefix="/progress", tags=["progress"])


class ProgressUpdate(BaseModel):
    scenario_id: str
    lang: str = "fr"
    steps_completed: int
    total_steps: int = 5


@router.get("/")
async def get_all_progress():
    """Return progress for all scenarios."""
    async with SessionLocal() as db:
        result = await db.execute(select(SessionRecord))
        records = result.scalars().all()
        return {
            "sessions": [
                {
                    "id": r.id,
                    "scenario_id": r.scenario_id,
                    "lang": r.lang,
                    "steps_completed": r.steps_completed,
                    "total_steps": r.total_steps,
                }
                for r in records
            ]
        }


@router.get("/{scenario_id}")
async def get_scenario_progress(scenario_id: str, lang: str = "fr"):
    """Return progress for a specific scenario."""
    async with SessionLocal() as db:
        result = await db.execute(
            select(SessionRecord).where(
                SessionRecord.scenario_id == scenario_id,
                SessionRecord.lang == lang,
            )
        )
        record = result.scalar_one_or_none()
        if not record:
            return {"scenario_id": scenario_id, "lang": lang, "steps_completed": 0, "total_steps": 5}
        return {
            "scenario_id": record.scenario_id,
            "lang": record.lang,
            "steps_completed": record.steps_completed,
            "total_steps": record.total_steps,
        }


@router.post("/")
async def upsert_progress(body: ProgressUpdate):
    """Create or update progress for a scenario."""
    async with SessionLocal() as db:
        result = await db.execute(
            select(SessionRecord).where(
                SessionRecord.scenario_id == body.scenario_id,
                SessionRecord.lang == body.lang,
            )
        )
        record = result.scalar_one_or_none()
        if record:
            await db.execute(
                update(SessionRecord)
                .where(SessionRecord.id == record.id)
                .values(
                    steps_completed=body.steps_completed,
                    total_steps=body.total_steps,
                )
            )
        else:
            db.add(
                SessionRecord(
                    scenario_id=body.scenario_id,
                    lang=body.lang,
                    steps_completed=body.steps_completed,
                    total_steps=body.total_steps,
                )
            )
        await db.commit()
    return {"status": "ok"}


@router.delete("/{scenario_id}")
async def reset_progress(scenario_id: str, lang: str = "fr"):
    """Reset progress for a scenario."""
    async with SessionLocal() as db:
        result = await db.execute(
            select(SessionRecord).where(
                SessionRecord.scenario_id == scenario_id,
                SessionRecord.lang == lang,
            )
        )
        record = result.scalar_one_or_none()
        if record:
            await db.delete(record)
            await db.commit()
    return {"status": "reset"}
