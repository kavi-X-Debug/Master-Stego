import os
from typing import Dict, Any

from master_stego.utils.subprocess_utils import run_command


def analyze(file_path: str, session_dir: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {"available": True, "info": None, "extract": None}

    info_result = run_command(["steghide", "info", file_path, "-p", ""], cwd=session_dir, timeout=60)
    if info_result["stderr"] == "command not found" or info_result["returncode"] is None:
        result["available"] = False
        result["info"] = {
            "returncode": info_result["returncode"],
            "stdout": "",
            "stderr": "steghide not installed on server",
        }
        result["extract"] = None
        return result

    result["info"] = {
        "returncode": info_result["returncode"],
        "stdout": info_result["stdout"],
        "stderr": info_result["stderr"],
    }

    out_name = "steghide_extracted"
    out_path = os.path.join(session_dir, out_name)
    extract_result = run_command(
        ["steghide", "extract", "-sf", file_path, "-p", "", "-xf", out_name],
        cwd=session_dir,
        timeout=120,
    )
    extract_info: Dict[str, Any] = {
        "returncode": extract_result["returncode"],
        "stdout": extract_result["stdout"],
        "stderr": extract_result["stderr"],
    }
    if os.path.exists(out_path):
        extract_info["extracted_file"] = out_name
    result["extract"] = extract_info

    return result
