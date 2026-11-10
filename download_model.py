"""Laedt ein faster-whisper-Modell in den lokalen models/-Ordner."""
import sys
from pathlib import Path

from huggingface_hub import snapshot_download

name = sys.argv[1] if len(sys.argv) > 1 else "large-v3"
target = Path(__file__).resolve().parent / "models" / name
snapshot_download(f"Systran/faster-whisper-{name}", local_dir=target)
print(f"Modell gespeichert in {target}")
