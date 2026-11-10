# Swiss German Transcription Tool (100% Local)

Einfaches GUI, das Schweizerdeutsch-Audio lokal mit Whisper (faster-whisper) in Hochdeutsch transkribiert. Keine Daten verlassen den Rechner.

## Setup (macOS)

```bash
brew install python-tk@3.14
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python download_model.py large-v3   # einmalig, ca. 3 GB nach models/ (nicht in Git)
python transcriber.py
```

Datei wählen, Modell wählen, "Transkribieren". Ergebnis: `.txt` und `.srt` neben der Quelldatei.
Modelle liegen im Ordner `models/` und werden dort bevorzugt geladen.
