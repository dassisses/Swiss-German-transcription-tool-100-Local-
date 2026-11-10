"""Macht aus einer rohen Whisper-Transkription (eine Zeile pro Segment) einen lesbaren Fliesstext.

Aufruf: python clean_transcript.py eingabe.txt [ausgabe.txt]
"""
import re
import sys
from pathlib import Path

SENTENCES_PER_PARAGRAPH = 5


def clean(text: str) -> str:
    joined = re.sub(r"\s+", " ", text.replace("\n", " ")).strip()
    sentences = re.split(r"(?<=[.!?])\s+", joined)

    out, last = [], None
    for s in sentences:
        key = re.sub(r"\W+", "", s.lower())
        if not key or key == last:  # Whisper-Wiederholungen entfernen
            continue
        out.append(s)
        last = key

    paragraphs = [
        " ".join(out[i:i + SENTENCES_PER_PARAGRAPH])
        for i in range(0, len(out), SENTENCES_PER_PARAGRAPH)
    ]
    return "\n\n".join(paragraphs) + "\n"


if __name__ == "__main__":
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_name(src.stem + "_sauber.txt")
    dst.write_text(clean(src.read_text(encoding="utf-8")), encoding="utf-8")
    print(f"Gespeichert: {dst}")
