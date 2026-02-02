from typing import Dict, Any

from master_stego.utils.subprocess_utils import run_command


def analyze(file_path: str) -> Dict[str, Any]:
    cmd_result = run_command(["zsteg", "-a", file_path], timeout=300)
    stderr = cmd_result["stderr"]
    available = not (stderr == "command not found" or cmd_result["returncode"] is None)
    return {
        "available": available,
        "returncode": cmd_result["returncode"],
        "stdout": cmd_result["stdout"],
        "stderr": stderr,
    }
