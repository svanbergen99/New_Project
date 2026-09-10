from __future__ import annotations

import json
import os
import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response

ROOT = Path(__file__).resolve().parent
app = FastAPI(title="KCD Visual Lab", version="1.0")

ELEVENLABS_API_KEY = (
    os.getenv("ELEVENLABS_API_KEY", "").strip()
    or os.getenv("Elevenlabs", "").strip()
)
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM").strip()
KCD_ASSET_ORIGIN = os.getenv(
    "KCD_ASSET_ORIGIN",
    "https://kcd-chat-production-6c70.up.railway.app",
).rstrip("/")

INTRO_SCRIPT = (
    "Hé! Welkom bij KCD. Ik ben KC-Dee, Kay Cee Dee. "
    "Ik ben een tijdje op vakantie geweest. Zon, zee, even opladen... je kent het wel. "
    "Maar eerlijk? Helemaal stilzitten is niet echt mijn ding. "
    "Tussen de palmbomen door heb ik vooral nagedacht over hoe ik KCD slimmer, sneller en fijner kan maken. "
    "Betere antwoorden. Slimmere tools. Meer overzicht. En vooral: hoe ik jullie straks nog beter kan helpen. "
    "Achter de schermen wordt gewerkt aan tekst, voice, video, verkeer, roosters en nog veel meer. "
    "Op mijn nieuwe desktop staat nu misschien nog niet zoveel... maar geef ons nog heel even. "
    "De koffers zijn bijna gepakt, mijn zonnebril kan bijna af... en ik ben bijna terug van vakantie. "
    "Tot heel snel bij KCD!"
)

_audio_cache: bytes | None = None
_audio_lock = threading.Lock()
_asset_cache: dict[str, tuple[bytes, str]] = {}
_asset_lock = threading.Lock()
ALLOWED_ASSETS = {
    "kc-dee.webp",
    "emoji-sheet-1.webp",
    "emoji-sheet-2.webp",
    "emoji-sheet-3.webp",
    "emoji-sheet-4.webp",
}


def _request(url: str, *, method: str = "GET", headers: dict[str, str] | None = None, body: bytes | None = None, timeout: int = 60):
    req = urllib.request.Request(url, method=method, headers=headers or {}, data=body)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status, response.read(), dict(response.headers.items())
    except urllib.error.HTTPError as error:
        return error.code, error.read(), dict(error.headers.items() if error.headers else [])
    except urllib.error.URLError as error:
        raise RuntimeError("Upstream service is niet bereikbaar.") from error


def _build_intro_audio() -> bytes:
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ElevenLabs is niet geconfigureerd.")
    voice_id = urllib.parse.quote(ELEVENLABS_VOICE_ID)
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128"
    payload = json.dumps({
        "text": INTRO_SCRIPT,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.34,
            "similarity_boost": 0.78,
            "style": 0.58,
            "use_speaker_boost": True,
        },
    }).encode("utf-8")
    status, data, _ = _request(
        url,
        method="POST",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "accept": "audio/mpeg",
            "content-type": "application/json",
        },
        body=payload,
        timeout=100,
    )
    if status >= 400 or not data:
        raise RuntimeError(f"Voice provider gaf HTTP {status}.")
    return data


@app.get("/")
def index():
    return FileResponse(ROOT / "index.html", media_type="text/html", headers={"Cache-Control": "no-cache"})


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "kcd-visual-lab",
        "voiceConfigured": bool(ELEVENLABS_API_KEY),
        "voiceModel": "eleven_multilingual_v2",
        "assetProxy": True,
    }


@app.get("/api/intro-voice")
def intro_voice():
    global _audio_cache
    if _audio_cache is None:
        with _audio_lock:
            if _audio_cache is None:
                try:
                    _audio_cache = _build_intro_audio()
                except RuntimeError as error:
                    raise HTTPException(status_code=503, detail=str(error)) from error
    return Response(
        content=_audio_cache,
        media_type="audio/mpeg",
        headers={
            "Cache-Control": "public, max-age=86400",
            "X-Content-Type-Options": "nosniff",
        },
    )


@app.get("/assets/{name}")
def kcd_asset(name: str):
    if name not in ALLOWED_ASSETS:
        raise HTTPException(status_code=404, detail="Asset niet gevonden.")
    cached = _asset_cache.get(name)
    if cached is None:
        with _asset_lock:
            cached = _asset_cache.get(name)
            if cached is None:
                status, data, headers = _request(f"{KCD_ASSET_ORIGIN}/assets/{name}", timeout=25)
                if status >= 400 or not data:
                    raise HTTPException(status_code=502, detail="KCD asset kon niet worden geladen.")
                content_type = headers.get("Content-Type", headers.get("content-type", "image/webp"))
                cached = (data, content_type)
                _asset_cache[name] = cached
    data, content_type = cached
    return Response(
        content=data,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=86400", "X-Content-Type-Options": "nosniff"},
    )
