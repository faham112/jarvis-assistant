import os, shutil, subprocess
MODEL = os.getenv("MJ_WHISPER_MODEL", "tiny")

def _whisper_cli(path):
    bin_ = shutil.which("whisper")
    if not bin_:
        return ""
    out_dir = os.path.dirname(path) or "/tmp"
    try:
        subprocess.run([bin_, path, "--model", MODEL, "--language", "ur", "--output_format", "txt", "--output_dir", out_dir], check=True, timeout=180, capture_output=True)
        txt = os.path.join(out_dir, os.path.splitext(os.path.basename(path))[0] + ".txt")
        if os.path.isfile(txt):
            return open(txt, encoding="utf-8", errors="replace").read().strip()
    except Exception:
        return ""
    return ""

def _faster(path):
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel(MODEL, device="cpu", compute_type="int8")
        segs, _ = model.transcribe(path, language="ur")
        return " ".join(s.text for s in segs).strip()
    except Exception:
        return ""

def _google(path):
    try:
        import speech_recognition as sr
        wav = path if path.endswith(".wav") else path + ".wav"
        if wav != path:
            os.system('ffmpeg -y -i "%s" -ar 16000 -ac 1 "%s" >/dev/null 2>&1' % (path, wav))
        r = sr.Recognizer()
        with sr.AudioFile(wav) as src:
            audio = r.record(src)
        try:
            return r.recognize_google(audio, language="ur-PK")
        except Exception:
            return r.recognize_google(audio, language="en-US")
    except Exception:
        return ""

def transcribe(path):
    for fn in (_faster, _whisper_cli, _google):
        text = fn(path)
        if text:
            return text
    return ""
