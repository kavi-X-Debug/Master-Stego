from typing import Dict, Any

from PIL import Image, ExifTags

from master_stego.utils.subprocess_utils import run_command


def analyze(file_path: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"exiftool": None, "pillow": None}

    cmd_result = run_command(["exiftool", "-json", file_path])
    if cmd_result["stderr"].strip() == "command not found" or cmd_result["returncode"] is None:
        result["exiftool"] = {"available": False, "error": "exiftool not installed on server"}
    elif cmd_result["returncode"] == 0:
        try:
            import json

            parsed = json.loads(cmd_result["stdout"])
            if isinstance(parsed, list) and parsed:
                result["exiftool"] = {"available": True, "data": parsed[0]}
            else:
                result["exiftool"] = {"available": True, "data": {}}
        except Exception:
            result["exiftool"] = {
                "available": True,
                "error": "failed to parse exiftool output",
            }
    else:
        if cmd_result["stderr"]:
            result["exiftool"] = {
                "available": True,
                "error": cmd_result["stderr"].strip(),
            }

    try:
        with Image.open(file_path) as img:
            exif_raw = img._getexif() or {}
        exif_data = {}
        for tag_id, value in exif_raw.items():
            tag = ExifTags.TAGS.get(tag_id, str(tag_id))
            exif_data[tag] = value
        result["pillow"] = exif_data
    except Exception:
        result["pillow"] = None

    return result
