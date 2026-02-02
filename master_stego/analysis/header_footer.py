import os
from typing import Dict, Any


def analyze(file_path: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "file_type": None,
        "valid_header": None,
        "valid_footer": None,
        "details": {},
    }

    try:
        with open(file_path, "rb") as f:
            data = f.read()
    except Exception as exc:
        result["details"]["error"] = str(exc)
        return result

    ext = os.path.splitext(file_path.lower())[1]
    result["file_type"] = ext

    if ext in [".jpg", ".jpeg"]:
        result["valid_header"] = data.startswith(b"\xFF\xD8")
        result["valid_footer"] = data.endswith(b"\xFF\xD9")
    elif ext == ".png":
        png_sig = b"\x89PNG\r\n\x1a\n"
        result["valid_header"] = data.startswith(png_sig)
        result["valid_footer"] = b"IEND" in data[-1024:]
    elif ext == ".bmp":
        result["valid_header"] = data.startswith(b"BM")
        result["valid_footer"] = True
    else:
        result["valid_header"] = None
        result["valid_footer"] = None

    return result

