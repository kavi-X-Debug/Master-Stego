import os
from typing import Dict, Any

from PIL import Image


def analyze(file_path: str, session_id: str, session_dir: str) -> Dict[str, Any]:
    output = {"channels": {}}

    try:
        with Image.open(file_path) as img:
            img = img.convert("RGBA")
            r, g, b, a = img.split()

            mapping = {"r": r, "g": g, "b": b, "a": a}
            for name, channel in mapping.items():
                filename = f"channel_{name.upper()}.png"
                out_path = os.path.join(session_dir, filename)
                channel.save(out_path)
                output["channels"][name] = {
                    "filename": filename,
                    "url": f"/api/session/{session_id}/files/{filename}",
                }
    except Exception as exc:
        output["error"] = str(exc)

    return output

