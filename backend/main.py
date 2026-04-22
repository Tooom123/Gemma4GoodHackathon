from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import chat, scenarios, progress, tts, whisper


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: nothing blocking at this stage
    yield
    # Shutdown: clean up resources here in future


app = FastAPI(
    title="LangBridge API",
    description="Offline multilingual language learning via Gemma 4 simulations",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(scenarios.router)
app.include_router(progress.router)
app.include_router(tts.router)
app.include_router(whisper.router)


@app.get("/")
async def root():
    return {"name": "LangBridge API", "version": "0.1.0", "status": "ok"}
