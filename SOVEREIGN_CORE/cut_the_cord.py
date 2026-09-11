from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = os.getenv("KCD_SOVEREIGN_URL", "http://127.0.0.1:8000").rstrip("/")


def get_json(path: str, timeout: int = 5):
    request = urllib.request.Request(BASE_URL + path, method="GET")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.status, json.loads(response.read().decode("utf-8") or "{}")


def post_json(path: str, payload: dict, timeout: int = 120):
    request = urllib.request.Request(
        BASE_URL + path,
        method="POST",
        data=json.dumps(payload).encode("utf-8"),
        headers={"content-type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.status, json.loads(response.read().decode("utf-8") or "{}")


def check(label: str, condition: bool, details="") -> bool:
    mark = "PASS" if condition else "FAIL"
    print(f"[{mark}] {label}{': ' + str(details) if details else ''}")
    return condition


def main() -> int:
    passed = True
    try:
        status_code, status = get_json("/v1/sovereign/status")
    except Exception as error:
        print(f"[FAIL] Sovereign Core niet bereikbaar: {type(error).__name__}")
        return 2

    passed &= check("status endpoint", status_code == 200)
    passed &= check("sovereign mode actief", status.get("sovereignMode") is True)
    passed &= check("externe AI uit", status.get("externalAi") is False)
    passed &= check("geen provider fallbacks", status.get("providerFallbacks") == [])

    model = status.get("model") or {}
    passed &= check("model endpoint private", model.get("endpointPrivate") is True, model.get("endpoint"))
    passed &= check("lokale inference bereikbaar", model.get("reachable") is True)

    if model.get("reachable"):
        try:
            code, body = post_json(
                "/v1/chat/completions",
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": "Antwoord uitsluitend met: KCDEE-SOVEREIGN-OK",
                        }
                    ],
                    "temperature": 0.0,
                    "max_tokens": 32,
                },
            )
            text = ""
            try:
                text = str(body["choices"][0]["message"]["content"])
            except Exception:
                pass
            passed &= check("lokale chat inference", code == 200 and "KCDEE-SOVEREIGN-OK" in text, text[:120])
        except urllib.error.HTTPError as error:
            passed &= check("lokale chat inference", False, f"HTTP {error.code}")
        except Exception as error:
            passed &= check("lokale chat inference", False, type(error).__name__)

    print("\nCUT-THE-CORD:", "PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
