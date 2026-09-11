from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import socket
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="KC-Dee Sovereign Core", version="0.2.0")

MODEL_ENDPOINT = os.getenv("KCD_MODEL_ENDPOINT", "http://llama:8080").rstrip("/")
MODEL_NAME = os.getenv("KCD_MODEL_NAME", "kcdee-local").strip()
MODEL_FILE = os.getenv("KCD_MODEL_FILE", "/models/kcdee.gguf").strip()
MODEL_SHA256 = os.getenv("KCD_MODEL_SHA256", "").strip().lower()
ALLOWED_MODEL_HOSTS = {
    value.strip().lower()
    for value in os.getenv(
        "KCD_ALLOWED_MODEL_HOSTS",
        "llama,kcd-model,localhost,127.0.0.1,::1",
    ).split(",")
    if value.strip()
}

SYSTEM_PROMPT = os.getenv(
    "KCD_SYSTEM_PROMPT",
    "Je bent KC-Dee, de zelfstandige KCD-assistent. Antwoord duidelijk, compact en feitelijk. "
    "Doe geen beroep op externe AI-diensten. Als je iets niet weet, zeg dat.",
).strip()


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(system|user|assistant|tool)$")
    content: str = Field(min_length=1, max_length=20000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=64)
    temperature: float = Field(default=0.4, ge=0.0, le=2.0)
    max_tokens: int = Field(default=512, ge=1, le=4096)


def _is_private_ip(value: str) -> bool:
    try:
        ip = ipaddress.ip_address(value)
        return ip.is_private or ip.is_loopback or ip.is_link_local
    except ValueError:
        return False


def _endpoint_is_private() -> bool:
    parsed = urllib.parse.urlparse(MODEL_ENDPOINT)
    host = (parsed.hostname or "").lower()
    if parsed.scheme not in {"http", "https"} or not host:
        return False
    if host in ALLOWED_MODEL_HOSTS:
        return True
    if _is_private_ip(host):
        return True
    try:
        addresses = socket.getaddrinfo(host, parsed.port or 80, type=socket.SOCK_STREAM)
        if not addresses:
            return False
        return all(_is_private_ip(item[4][0]) for item in addresses)
    except OSError:
        return False


def _model_hash_status() -> dict[str, Any]:
    path = Path(MODEL_FILE)
    if not path.exists():
        return {"present": False, "verified": False, "path": MODEL_FILE}
    if not MODEL_SHA256:
        return {"present": True, "verified": False, "path": MODEL_FILE, "reason": "sha256_not_configured"}
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    actual = digest.hexdigest().lower()
    return {
        "present": True,
        "verified": actual == MODEL_SHA256,
        "path": MODEL_FILE,
        "sha256": actual,
    }


def _local_json(path: str, payload: dict[str, Any], timeout: int = 120) -> tuple[int, dict[str, Any]]:
    if not _endpoint_is_private():
        raise RuntimeError("Model endpoint is niet lokaal/private; sovereign mode weigert dit endpoint.")
    request = urllib.request.Request(
        MODEL_ENDPOINT + path,
        method="POST",
        data=json.dumps(payload).encode("utf-8"),
        headers={"content-type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8") or "{}")
            return response.status, body
    except urllib.error.HTTPError as error:
        try:
            body = json.loads(error.read().decode("utf-8") or "{}")
        except Exception:
            body = {}
        return error.code, body
    except urllib.error.URLError as error:
        raise RuntimeError("Lokale KC-Dee inference is niet bereikbaar.") from error


def _local_health() -> bool:
    if not _endpoint_is_private():
        return False
    for path in ("/health", "/v1/models"):
        try:
            request = urllib.request.Request(MODEL_ENDPOINT + path, method="GET")
            with urllib.request.urlopen(request, timeout=3) as response:
                if response.status < 500:
                    return True
        except Exception:
            continue
    return False


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "kcdee-sovereign-core",
        "sovereignMode": True,
        "externalProviderFallback": False,
        "modelEndpointPrivate": _endpoint_is_private(),
        "localInferenceReachable": _local_health(),
    }


@app.get("/v1/sovereign/status")
def sovereign_status(verify_model_hash: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {
        "sovereignMode": True,
        "externalAi": False,
        "providerFallbacks": [],
        "model": {
            "name": MODEL_NAME,
            "endpoint": MODEL_ENDPOINT,
            "endpointPrivate": _endpoint_is_private(),
            "reachable": _local_health(),
        },
    }
    if verify_model_hash:
        result["model"]["weights"] = _model_hash_status()
    return result


@app.post("/v1/chat/completions")
def chat(package: ChatRequest) -> dict[str, Any]:
    if not _endpoint_is_private():
        raise HTTPException(status_code=503, detail="Sovereign model endpoint is niet private.")

    messages = [item.model_dump() for item in package.messages]
    if not messages or messages[0]["role"] != "system":
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": package.temperature,
        "max_tokens": package.max_tokens,
        "stream": False,
    }
    try:
        status, body = _local_json("/v1/chat/completions", payload)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    if status >= 400:
        raise HTTPException(status_code=503, detail="Lokale KC-Dee inference gaf een fout.")

    return body
