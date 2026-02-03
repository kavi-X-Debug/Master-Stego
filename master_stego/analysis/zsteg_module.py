from typing import Dict, Any

from master_stego.utils.subprocess_utils import run_command


def analyze(file_path: str) -> Dict[str, Any]:
    cmd_result = run_command(["zsteg", "-a", file_path], timeout=300)
    stderr = cmd_result["stderr"] or ""
    available = not (stderr == "command not found" or cmd_result["returncode"] is None)

    cleaned_stderr = stderr
    if "undefined method `alpha_used?'" in stderr:
        lines = stderr.splitlines()
        useful = []
        for line in lines:
            s = line.strip()
            if s.startswith("[?]") or s.startswith("[!]") or "bytes of extra data after image end" in s:
                useful.append(line)
        if not useful:
            useful.append("zsteg encountered an internal error (alpha_used?); Ruby stack trace suppressed.")
        cleaned_stderr = "\n".join(useful)

    return {
        "available": available,
        "returncode": cmd_result["returncode"],
        "stdout": cmd_result["stdout"],
        "stderr": cleaned_stderr,
    }
