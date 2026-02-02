import os
from typing import Dict, Any, List

from master_stego.utils.subprocess_utils import run_command


def analyze(file_path: str, session_dir: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "summary": None,
        "stderr": None,
        "returncode": None,
        "available": True,
        "extracted_paths": [],
    }

    cmd_result = run_command(["binwalk", "-e", "-q", file_path], cwd=session_dir, timeout=120)
    result["returncode"] = cmd_result["returncode"]
    result["summary"] = cmd_result["stdout"]
    result["stderr"] = cmd_result["stderr"]

    if cmd_result["stderr"] == "command not found" or cmd_result["returncode"] is None:
        result["available"] = False
        result["summary"] = "binwalk not installed on server"
        return result

    extracted: List[str] = []
    for entry in os.listdir(session_dir):
        if entry.endswith(".extracted"):
            extracted_dir = os.path.join(session_dir, entry)
            for root, _, files in os.walk(extracted_dir):
                for f in files:
                    rel = os.path.relpath(os.path.join(root, f), session_dir)
                    extracted.append(rel.replace(os.sep, "/"))

    result["extracted_paths"] = extracted

    return result
