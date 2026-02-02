import os
from typing import Dict, Any

import numpy as np
from PIL import Image


def analyze(file_path: str, session_id: str, session_dir: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"planes": {}}

    try:
        with Image.open(file_path) as img:
            img = img.convert("RGBA")
            arr = np.array(img)

        channel_names = ["r", "g", "b", "a"]

        for idx, name in enumerate(channel_names):
            channel = arr[:, :, idx]
            for bit in range(8):
                mask = 1 << bit
                plane = ((channel & mask) > 0).astype("uint8") * 255
                out_img = Image.fromarray(plane, mode="L")
                filename = f"bitplane_{name}_{bit}.png"
                out_path = os.path.join(session_dir, filename)
                out_img.save(out_path)

                result["planes"].setdefault(name, {})
                result["planes"][name][str(bit)] = {
                    "filename": filename,
                    "url": f"/api/session/{session_id}/files/{filename}",
                }
    except Exception as exc:
        result["error"] = str(exc)

    return result

