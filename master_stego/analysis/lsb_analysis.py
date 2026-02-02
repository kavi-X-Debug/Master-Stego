from typing import Dict, Any

import numpy as np
from PIL import Image


def analyze(file_path: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"channels": {}, "combined": {}}

    try:
        with Image.open(file_path) as img:
            img = img.convert("RGBA")
            arr = np.array(img)
    except Exception as exc:
        result["error"] = str(exc)
        return result

    channel_names = ["r", "g", "b", "a"]
    for idx, name in enumerate(channel_names):
        channel = arr[:, :, idx]
        bits = channel & 1
        decoded = _bits_to_text(bits)
        result["channels"][name] = {
            "preview": decoded[:1024],
            "length": len(decoded),
        }

    rgb = arr[:, :, :3]
    r_lsb = (rgb[:, :, 0] & 1).flatten()
    g_lsb = (rgb[:, :, 1] & 1).flatten()
    b_lsb = (rgb[:, :, 2] & 1).flatten()

    interleaved_bits = []
    max_len = max(len(r_lsb), len(g_lsb), len(b_lsb))
    for i in range(max_len):
        if i < len(r_lsb):
            interleaved_bits.append(r_lsb[i])
        if i < len(g_lsb):
            interleaved_bits.append(g_lsb[i])
        if i < len(b_lsb):
            interleaved_bits.append(b_lsb[i])

    interleaved_bits = np.array(interleaved_bits, dtype=np.uint8)
    combined_text = _bits_to_text(interleaved_bits)
    result["combined"] = {
        "preview": combined_text[:1024],
        "length": len(combined_text),
    }

    return result


def _bits_to_text(bits_array) -> str:
    flat = bits_array.flatten()
    chars = []
    for i in range(0, len(flat), 8):
        byte = 0
        chunk = flat[i : i + 8]
        if len(chunk) < 8:
            break
        for bit in chunk:
            byte = (byte << 1) | int(bit)
        if 32 <= byte <= 126 or byte in (9, 10, 13):
            chars.append(chr(byte))
        else:
            chars.append(".")
    return "".join(chars)

