from typing import Dict, Any, List

from master_stego.utils.subprocess_utils import run_command


def analyze(file_path: str) -> Dict[str, Any]:
    ascii_strings = _run_strings(file_path, ["strings", "-a"])
    utf16_strings = _run_strings(file_path, ["strings", "-a", "-el"])

    return {
        "ascii": ascii_strings,
        "utf16": utf16_strings,
    }


def _run_strings(file_path: str, base_cmd: List[str]) -> Dict[str, Any]:
    cmd = base_cmd + [file_path]
    cmd_result = run_command(cmd, timeout=60)
    output_lines: List[str] = []

    if cmd_result["stdout"]:
        for line in cmd_result["stdout"].splitlines():
            if line.strip():
                output_lines.append(line.strip())

    stderr = cmd_result["stderr"].strip() if cmd_result["stderr"] else ""
    available = not (stderr == "command not found" or cmd_result["returncode"] is None)

    return {
        "cmd": cmd,
        "returncode": cmd_result["returncode"],
        "stderr": stderr,
        "available": available,
        "count": len(output_lines),
        "sample": output_lines[:500],
    }
