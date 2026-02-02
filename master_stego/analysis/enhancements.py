import os
from typing import Dict, Any

import cv2
from PIL import Image, ImageOps, ImageEnhance
import numpy as np


def analyze(file_path: str, session_id: str, session_dir: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"images": {}}

    try:
        with Image.open(file_path) as img:
            img = img.convert("RGB")

            inverted = ImageOps.invert(img)
            inverted_name = "enh_invert.png"
            inverted_path = os.path.join(session_dir, inverted_name)
            inverted.save(inverted_path)
            result["images"]["invert"] = {
                "filename": inverted_name,
                "url": f"/api/session/{session_id}/files/{inverted_name}",
            }

            enhancer = ImageEnhance.Contrast(img)
            contrasted = enhancer.enhance(2.0)
            contrast_name = "enh_contrast.png"
            contrast_path = os.path.join(session_dir, contrast_name)
            contrasted.save(contrast_path)
            result["images"]["contrast"] = {
                "filename": contrast_name,
                "url": f"/api/session/{session_id}/files/{contrast_name}",
            }
    except Exception as exc:
        result["error"] = str(exc)
        return result

    try:
        cv_img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        if cv_img is not None:
            _, thresh = cv2.threshold(cv_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            thresh_name = "enh_threshold.png"
            thresh_path = os.path.join(session_dir, thresh_name)
            cv2.imwrite(thresh_path, thresh)
            result["images"]["threshold"] = {
                "filename": thresh_name,
                "url": f"/api/session/{session_id}/files/{thresh_name}",
            }
    except Exception as exc:
        result.setdefault("threshold_error", str(exc))

    return result

