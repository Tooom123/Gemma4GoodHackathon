import os
import subprocess
import tempfile
from pathlib import Path

# Configurable via env vars — adapt to your OS/install path
WHISPER_BIN = os.getenv("WHISPER_BIN", "whisper-cpp")
WHISPER_MODEL = os.getenv(
    "WHISPER_MODEL",
    str(Path(__file__).parent.parent / "data" / "whisper" / "ggml-small.bin"),
)


async def transcribe(audio_bytes: bytes, suffix: str = ".webm") -> str:
    """
    Run whisper.cpp on audio_bytes, return transcription text.
    Writes audio to a temp file, calls the binary, reads stdout.
    Falls back gracefully if binary or model is missing.
    """
    _check_bin()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(audio_bytes)
        tmp_path = f.name
    try:
        result = subprocess.run(
            [
                WHISPER_BIN,
                "-m", WHISPER_MODEL,
                "-f", tmp_path,
                "--output-txt",
                "--no-timestamps",
                "-l", "auto",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            raise RuntimeError(f"whisper-cpp error: {result.stderr.strip()}")
        # whisper-cpp writes to <file>.txt — read it
        txt_path = tmp_path + ".txt"
        if Path(txt_path).exists():
            text = Path(txt_path).read_text(encoding="utf-8").strip()
            Path(txt_path).unlink(missing_ok=True)
            return text
        return result.stdout.strip()
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def _check_bin() -> None:
    if not _binary_available(WHISPER_BIN):
        raise RuntimeError(
            f"whisper-cpp binary not found at '{WHISPER_BIN}'. "
            "Build from https://github.com/ggerganov/whisper.cpp or set WHISPER_BIN env var."
        )
    if not Path(WHISPER_MODEL).exists():
        raise RuntimeError(
            f"Whisper model not found at '{WHISPER_MODEL}'. "
            "Download with: bash whisper.cpp/models/download-ggml-model.sh small"
        )


def _binary_available(name: str) -> bool:
    import shutil
    return shutil.which(name) is not None or Path(name).exists()
