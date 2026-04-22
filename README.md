# LangBridge

> Multilingual offline PWA helping refugees learn the local language through real-life simulations — powered by Gemma 4 running locally via Ollama.

Submitted to the **Gemma 4 Good Hackathon** (Kaggle × Google DeepMind, May 2026).

---

## What it does

LangBridge simulates everyday administrative situations (prefecture appointment, doctor visit, school enrollment, job interview) in dialogue form. The user plays themselves; Gemma 4 plays the counterpart. After each user reply, the model provides inline pedagogical feedback (grammar corrections, vocabulary hints, encouragement) as a structured JSON block.

Everything runs **offline** once the model is downloaded — no data leaves the device.

---

## Quick start

### Prerequisites

- [Ollama](https://ollama.com/) installed and running
- Python 3.11+
- Node.js 20+

### 1. Pull Gemma 4

```bash
# Lightweight (CPU-friendly, ~4 GB)
ollama pull gemma4:e4b

# Full quality (GPU recommended, ~16 GB)
ollama pull gemma4:26b
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

---

## Architecture

```
User browser (React PWA)
    ↕ SSE stream
FastAPI backend (port 8000)
    ↕ HTTP (local)
Ollama (port 11434)
    ↓
Gemma 4 (local weights)
```

Key design choices:
- **Streaming**: tokens appear word-by-word via Server-Sent Events — no 10-second wait
- **Offline-first**: Workbox service worker caches the app shell; Ollama serves the model locally
- **No iOS**: PWA targets Android Chrome and desktop browsers
- **SQLite**: all user data stays local (aiosqlite + SQLAlchemy async)

---

## Scenarios (MVP)

| # | Scenario | Language | Difficulty |
|---|----------|----------|------------|
| 1 | Prefecture appointment | French | Intermediate |
| 2 | GP medical consultation | French / English | Intermediate |
| 3 | School enrollment | French | Beginner |
| 4 | Job interview | French / English | Advanced |
| 5 | Supermarket / pharmacy | French | Beginner |
| 6 | Landlord phone call | French | Intermediate |

---

## Fine-tuning (Unsloth prize track)

See [`finetune/`](finetune/) for the QLoRA pipeline using Unsloth on `gemma4:26b`.  
Training data: OPUS-100 + FLORES-200 + synthetic administrative dialogues.

---

## License

Apache 2.0
