import os
import subprocess
import tempfile
import shutil
from pathlib import Path

PIPER_BIN = os.getenv("PIPER_BIN", "piper")

# Voice model paths — download from https://github.com/rhasspy/piper/releases
VOICE_MODELS: dict[str, str] = {
    "fr": os.getenv("PIPER_VOICE_FR", "fr_FR-upmc-medium.onnx"),
    "en": os.getenv("PIPER_VOICE_EN", "en_US-lessac-medium.onnx"),
    "ar": os.getenv("PIPER_VOICE_AR", "ar_JO-kareem-medium.onnx"),
    "es": os.getenv("PIPER_VOICE_ES", "es_ES-carlfm-x_low.onnx"),
}


async def synthesize(text: str, lang: str = "fr") -> bytes:
    """
    Synthesize text to WAV using Piper TTS binary.
    Returns raw WAV bytes.
    Falls back with RuntimeError if piper is not installed.
    """
    if not shutil.which(PIPER_BIN) and not Path(PIPER_BIN).exists():
        raise RuntimeError(
            f"piper binary not found at '{PIPER_BIN}'. "
            "Install from https://github.com/rhasspy/piper or set PIPER_BIN env var."
        )

    voice_model = VOICE_MODELS.get(lang, VOICE_MODELS["fr"])
    if not Path(voice_model).exists():
        raise RuntimeError(
            f"Piper voice model not found: '{voice_model}'. "
            "Download voice files from https://github.com/rhasspy/piper/releases"
        )

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as out_f:
        out_path = out_f.name

    try:
        proc = subprocess.run(
            [PIPER_BIN, "--model", voice_model, "--output_file", out_path],
            input=text,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"piper error: {proc.stderr.strip()}")
        return Path(out_path).read_bytes()
    finally:
        Path(out_path).unlink(missing_ok=True)
