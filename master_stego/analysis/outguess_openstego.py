from typing import Dict, Any

from master_stego.utils.subprocess_utils import run_command


def analyze(file_path: str, session_dir: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "outguess": {},
        "openstego": {},
    }

    outguess_info = run_command(["outguess", "-h"])
    if outguess_info["stderr"] == "command not found":
        result["outguess"] = {"available": False, "error": "outguess not installed"}
    else:
        extract = run_command(["outguess", "-r", file_path, "outguess_extracted"], cwd=session_dir)
        result["outguess"] = {
            "available": True,
            "returncode": extract["returncode"],
            "stdout": extract["stdout"],
            "stderr": extract["stderr"],
        }

    openstego_info = run_command(["openstego", "-help"])
    if openstego_info["stderr"] == "command not found":
        result["openstego"] = {"available": False, "error": "openstego not installed"}
    else:
        extract = run_command(
            ["openstego", "extract", "-sf", file_path, "-p", ""],
            cwd=session_dir,
            timeout=300,
        )
        result["openstego"] = {
            "available": True,
            "returncode": extract["returncode"],
            "stdout": extract["stdout"],
            "stderr": extract["stderr"],
        }

    return result
