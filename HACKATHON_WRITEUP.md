# LangBridge — Hackathon Technical Write-up

**Competition:** Gemma 4 Good Hackathon (Kaggle × Google DeepMind)  
**Category:** Future of Education  
**Prize tracks:** General + Unsloth Special Prize (QLoRA fine-tuning)

---

## Problem Statement

Millions of refugees and migrants arrive in a new country without mastering the local language. Existing language learning tools (Duolingo, Babbel) are:

- **Gamified but shallow** — they don't teach how to navigate real administrative situations
- **Cloud-dependent** — unusable without a stable internet connection
- **Not adapted to urgent needs** — prefecture appointments, medical emergencies, school enrollment

LangBridge addresses this gap with realistic dialogue simulations, inline pedagogical correction, and **fully offline operation**.

---

## Solution: LangBridge

A Progressive Web App (PWA) that simulates real-life administrative conversations using Gemma 4 running locally via Ollama. The user practices by playing themselves; Gemma 4 plays the counterpart (civil servant, doctor, pharmacist, landlord, HR manager).

### Key differentiators

| Feature | LangBridge | Duolingo | Generic chatbot |
|---------|-----------|----------|-----------------|
| Real admin scenarios | ✅ | ❌ | Partial |
| Works offline | ✅ | ❌ | ❌ |
| Inline corrections | ✅ | Partial | ❌ |
| No data sent externally | ✅ | ❌ | ❌ |
| Voice input/output | ✅ | ✅ | Partial |
| Free forever | ✅ | Freemium | API cost |

---

## Technical Architecture

```
User Browser (PWA)
    │
    │  SSE stream (tokens appear in real-time)
    ▼
FastAPI Backend (port 8000)
    │
    ├── POST /chat/stream  →  Ollama streaming API
    ├── POST /whisper/transcribe  →  whisper.cpp binary (local)
    ├── POST /tts  →  Piper TTS binary (local)
    ├── GET  /scenarios/{lang}/{id}  →  JSON files on disk
    └── CRUD /progress  →  SQLite (aiosqlite + SQLAlchemy async)
    │
    ▼
Ollama (port 11434)
    │
    ▼
Gemma 4 (local weights, no internet required)
```

### Why Gemma 4?

Gemma 4 was chosen because:
1. **Native function calling** — we use structured JSON output for pedagogy blocks (`{"corrections": [...], "vocabulary": [...], "encouragement": "..."}`)
2. **Multilingual strength** — French, English, Arabic, Spanish in a single model
3. **Efficient quantization** — `gemma4:e4b` runs on 4 GB RAM (CPU), making it accessible on low-end hardware
4. **Local inference via Ollama** — zero API cost, zero latency to external servers, GDPR-compliant by design

### Gemma 4 usage in LangBridge

Gemma 4 plays **three distinct roles simultaneously** in each conversation turn:

1. **Interlocutor** — speaks as the civil servant / doctor / pharmacist in the target language
2. **Pedagogue** — outputs a structured JSON block with grammar corrections and vocabulary hints
3. **Scenario manager** — advances the conversation through defined steps naturally

This is achieved through a carefully engineered system prompt per scenario, not fine-tuning (though fine-tuning improves quality — see below).

### Streaming implementation

Gemma 4 responses stream token-by-token via Server-Sent Events:

```
Backend: Ollama /api/chat (stream=true) → SSE → Frontend
Frontend: ReadableStream + TextDecoder → useState update per token
```

This eliminates the "10-second white screen" problem typical of LLM apps.

---

## Offline Architecture

LangBridge is offline-first by design:

| Component | Offline behavior |
|-----------|-----------------|
| React app shell | Served from Workbox service worker cache |
| Scenario JSON files | Cached via StaleWhileRevalidate |
| Gemma 4 inference | Ollama serves local model weights |
| Voice input | whisper.cpp runs locally (no cloud) |
| Voice output | Piper TTS runs locally (no cloud) |
| Progress data | SQLite on local disk |

Once Ollama and the model weights are downloaded, **zero bytes leave the device**.

---

## Scenarios Implemented (MVP)

| # | Scenario | Language | Difficulty | Real-world impact |
|---|----------|----------|------------|-------------------|
| 1 | Prefecture appointment | French | Intermediate | Residence permit renewal |
| 2 | GP medical consultation | French | Intermediate | Healthcare access |
| 3 | School enrollment | French | Beginner | Children's education |
| 4 | Job interview | French | Advanced | Economic integration |
| 5 | Pharmacy | French | Beginner | Basic healthcare |
| 6 | Landlord phone call | French | Intermediate | Housing access |

Each scenario includes: context, role prompt, key vocabulary (6-8 words), sample phrases, and 5 progression steps tracked in SQLite.

---

## Fine-tuning (Unsloth Prize Track)

### Why fine-tune?

The baseline Gemma 4 26B is already multilingual and capable. Fine-tuning adds:
- **Role consistency** — the model stays in character as a French civil servant throughout
- **JSON compliance** — the pedagogy block format (`{"corrections": [...]}`) is emitted reliably after every user turn
- **Administrative vocabulary accuracy** — fewer hallucinations on actual French bureaucratic procedures

### Pipeline

```python
# Unsloth QLoRA — 4-bit quantization
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="google/gemma-4-12b-it",
    max_seq_length=2048,
    load_in_4bit=True,
)
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,
    use_gradient_checkpointing=True,
)
```

### Dataset

| Source | Size | License |
|--------|------|---------|
| Synthetic admin dialogues (LangBridge) | 5 scenarios × ~10 turns | Apache 2.0 |
| OPUS-100 (Helsinki-NLP/opus-100) | up to 500 samples | CC-BY 4.0 |

Training: 80% / Validation: 20%  
Format: ShareGPT → HuggingFace chat template

### Expected metrics

| Metric | Baseline | Fine-tuned |
|--------|----------|------------|
| Perplexity (admin val set) | ~45 | ~18 |
| JSON format compliance | ~60% | ~95% |
| Role consistency (subjective) | Good | Excellent |

See `finetune/eval_results.json` for actual numbers post-training.

---

## Privacy & Ethics

- **No data collection** — all processing is local; no telemetry, no analytics
- **GDPR-compliant by design** — impossible to breach what is never sent
- **Accessible** — works on Android (PWA), Windows 10/11, Ubuntu 22.04
- **Low-resource hardware** — `gemma4:e4b` runs on CPU with 4 GB RAM
- **Multilingual** — French, English, Arabic, Spanish (expandable to any Ollama-supported language)
- **Open source** — Apache 2.0 license, public GitHub repository

---

## Repository Structure

```
langbridge/
├── backend/           FastAPI + Ollama client + SQLite
├── frontend/          React 18 + Vite + TailwindCSS + PWA
├── finetune/          Unsloth QLoRA pipeline (prepare + train + evaluate)
├── README.md          Installation guide (Windows + Ubuntu)
└── HACKATHON_WRITEUP.md  This document
```

---

## Installation (reproducible)

```bash
# 1. Clone and install dependencies
git clone https://github.com/Tooom123/Gemma4GoodHackathon
cd Gemma4GoodHackathon

# 2. Start Ollama and pull Gemma 4
ollama pull gemma4:e4b   # lightweight (4 GB, CPU-friendly)

# 3. Backend
cd backend && pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000

# 4. Frontend
cd ../frontend && npm install && npm run dev

# 5. Open http://localhost:5173
```

All steps work on **Windows 10/11** (with Ollama for Windows) and **Ubuntu 22.04**.

---

*Built in 4 weeks for the Gemma 4 Good Hackathon. Apache 2.0.*
