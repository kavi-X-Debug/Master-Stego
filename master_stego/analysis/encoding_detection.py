import base64
import binascii
import re
from typing import Dict, Any, List


def analyze(strings_result: Dict[str, Any]) -> Dict[str, Any]:
    candidates: List[str] = []
    for key in ("ascii", "utf16"):
        section = strings_result.get(key) or {}
        sample = section.get("sample") or []
        candidates.extend(sample[:200])

    detected: Dict[str, Any] = {
        "base64": [],
        "hex": [],
        "binary": [],
        "rot13": [],
    }

    for s in candidates:
        s_strip = s.strip()
        if not s_strip:
            continue

        if _looks_base64(s_strip):
            decoded = _safe_b64decode(s_strip)
            if decoded:
                detected["base64"].append({"source": s_strip, "decoded": decoded[:1024]})

        if _looks_hex(s_strip):
            decoded = _safe_hexdecode(s_strip)
            if decoded:
                detected["hex"].append({"source": s_strip, "decoded": decoded[:1024]})

        if _looks_binary(s_strip):
            decoded = _binary_to_text(s_strip)
            if decoded:
                detected["binary"].append({"source": s_strip, "decoded": decoded[:1024]})

        rot = _rot13(s_strip)
        if rot and rot != s_strip:
            detected["rot13"].append({"source": s_strip, "decoded": rot[:1024]})

    return detected


def _looks_base64(s: str) -> bool:
    if len(s) < 16 or len(s) % 4 != 0:
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9+/]+=*", s))


def _safe_b64decode(s: str) -> str:
    try:
        data = base64.b64decode(s, validate=True)
        return _bytes_to_printable(data)
    except Exception:
        return ""


def _looks_hex(s: str) -> bool:
    if len(s) < 16 or len(s) % 2 != 0:
        return False
    return bool(re.fullmatch(r"[0-9a-fA-F]+", s))


def _safe_hexdecode(s: str) -> str:
    try:
        data = binascii.unhexlify(s)
        return _bytes_to_printable(data)
    except Exception:
        return ""


def _looks_binary(s: str) -> bool:
    if len(s) < 8:
        return False
    return bool(re.fullmatch(r"[01]+", s))


def _binary_to_text(s: str) -> str:
    bits = s.strip()
    chars = []
    for i in range(0, len(bits), 8):
        chunk = bits[i : i + 8]
        if len(chunk) < 8:
            break
        try:
            val = int(chunk, 2)
        except ValueError:
            break
        if 32 <= val <= 126 or val in (9, 10, 13):
            chars.append(chr(val))
        else:
            chars.append(".")
    return "".join(chars)


def _rot13(s: str) -> str:
    result_chars = []
    for c in s:
        if "a" <= c <= "z":
            result_chars.append(chr((ord(c) - ord("a") + 13) % 26 + ord("a")))
        elif "A" <= c <= "Z":
            result_chars.append(chr((ord(c) - ord("A") + 13) % 26 + ord("A")))
        else:
            result_chars.append(c)
    return "".join(result_chars)


def _bytes_to_printable(data: bytes) -> str:
    text = []
    for b in data:
        if 32 <= b <= 126 or b in (9, 10, 13):
            text.append(chr(b))
        else:
            text.append(".")
    return "".join(text)

