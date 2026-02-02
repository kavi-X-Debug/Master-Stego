import os
import hashlib
from PIL import Image


def analyze(file_path):
    info = {}
    try:
        stat = os.stat(file_path)
        info["size_bytes"] = stat.st_size
    except Exception:
        info["size_bytes"] = None

    try:
        with open(file_path, "rb") as f:
            data = f.read()
        info["sha256"] = hashlib.sha256(data).hexdigest()
        info["md5"] = hashlib.md5(data).hexdigest()
    except Exception:
        info["sha256"] = None
        info["md5"] = None

    try:
        with Image.open(file_path) as img:
            info["format"] = img.format
            info["mode"] = img.mode
            info["size"] = {"width": img.width, "height": img.height}
    except Exception:
        info["format"] = None
        info["mode"] = None
        info["size"] = None

    return info

