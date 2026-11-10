"""Swiss German -> Standard German transcription tool (100% local, Whisper)."""
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

MODELS = ["large-v3", "medium", "small", "base"]
MODELS_DIR = Path(__file__).resolve().parent / "models"


def fmt_ts(t: float) -> str:
    h, rem = divmod(int(t), 3600)
    m, s = divmod(rem, 60)
    ms = int((t - int(t)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def transcribe(path, model_name, language, on_progress, on_text):
    from faster_whisper import WhisperModel

    on_progress(0, "Modell wird geladen (beim ersten Mal Download)…")
    local = MODELS_DIR / model_name
    # Lokaler Ordner hat Vorrang; sonst Download in den models/-Ordner
    model = WhisperModel(
        str(local) if local.is_dir() else model_name,
        device="cpu",
        compute_type="int8",
        download_root=str(MODELS_DIR),
    )
    segments, info = model.transcribe(
        path,
        language=None if language == "auto" else language,
        task="transcribe",
        vad_filter=True,
        beam_size=5,
    )
    result = []
    for seg in segments:
        result.append(seg)
        on_text(seg.text.strip())
        if info.duration:
            on_progress(min(seg.end / info.duration, 1) * 100, "Transkribiere…")
    return result


def write_outputs(audio_path, segments):
    base = Path(audio_path).with_suffix("")
    txt = base.with_suffix(".txt")
    srt = base.with_suffix(".srt")
    txt.write_text("\n".join(s.text.strip() for s in segments), encoding="utf-8")
    with srt.open("w", encoding="utf-8") as f:
        for i, s in enumerate(segments, 1):
            f.write(f"{i}\n{fmt_ts(s.start)} --> {fmt_ts(s.end)}\n{s.text.strip()}\n\n")
    return txt, srt


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Schweizerdeutsch → Hochdeutsch (Whisper, lokal)")
        self.geometry("720x560")
        self.q = queue.Queue()
        self.file = tk.StringVar()
        self.model = tk.StringVar(value=MODELS[0])
        self.lang = tk.StringVar(value="de")

        pad = {"padx": 10, "pady": 6}
        top = ttk.Frame(self)
        top.pack(fill="x", **pad)
        ttk.Entry(top, textvariable=self.file).pack(side="left", fill="x", expand=True)
        ttk.Button(top, text="Datei wählen…", command=self.pick).pack(side="left", padx=(6, 0))

        opts = ttk.Frame(self)
        opts.pack(fill="x", **pad)
        ttk.Label(opts, text="Modell:").pack(side="left")
        ttk.Combobox(opts, textvariable=self.model, values=MODELS, width=16,
                     state="readonly").pack(side="left", padx=6)
        ttk.Label(opts, text="Sprache:").pack(side="left", padx=(12, 0))
        ttk.Combobox(opts, textvariable=self.lang, values=["de", "auto"], width=6,
                     state="readonly").pack(side="left", padx=6)
        self.btn = ttk.Button(opts, text="Transkribieren", command=self.start)
        self.btn.pack(side="right")

        self.bar = ttk.Progressbar(self, maximum=100)
        self.bar.pack(fill="x", **pad)
        self.status = ttk.Label(self, text="Bereit.")
        self.status.pack(anchor="w", padx=10)

        self.out = tk.Text(self, wrap="word")
        self.out.pack(fill="both", expand=True, **pad)
        self.after(100, self.poll)

    def pick(self):
        # macOS-Tk greyt Dateien mit Muster-Strings aus, daher keine Filter
        p = filedialog.askopenfilename(title="Audio-/Videodatei wählen")
        if p:
            self.file.set(p)

    def start(self):
        path = self.file.get()
        if not path or not Path(path).is_file():
            messagebox.showwarning("Hinweis", "Bitte eine gültige Datei wählen.")
            return
        self.btn.state(["disabled"])
        self.out.delete("1.0", "end")
        threading.Thread(target=self.worker, args=(path,), daemon=True).start()

    def worker(self, path):
        try:
            segs = transcribe(
                path, self.model.get(), self.lang.get(),
                lambda v, m: self.q.put(("progress", v, m)),
                lambda t: self.q.put(("text", t)),
            )
            txt, srt = write_outputs(path, segs)
            self.q.put(("done", f"Fertig. Gespeichert: {txt.name}, {srt.name}"))
        except Exception as e:
            self.q.put(("error", str(e)))

    def poll(self):
        while not self.q.empty():
            kind, *a = self.q.get()
            if kind == "progress":
                self.bar["value"] = a[0]
                self.status.config(text=a[1])
            elif kind == "text":
                self.out.insert("end", a[0] + "\n")
                self.out.see("end")
            elif kind == "done":
                self.bar["value"] = 100
                self.status.config(text=a[0])
                self.btn.state(["!disabled"])
            elif kind == "error":
                self.status.config(text="Fehler")
                self.btn.state(["!disabled"])
                messagebox.showerror("Fehler", a[0])
        self.after(100, self.poll)


if __name__ == "__main__":
    App().mainloop()
