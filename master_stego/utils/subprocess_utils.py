import subprocess
from typing import List, Optional, Dict, Any


def run_command(cmd: List[str], cwd: Optional[str] = None, timeout: int = 30) -> Dict[str, Any]:
    try:
        completed = subprocess.run(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "cmd": cmd,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "cmd": cmd,
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": (exc.stderr or "") + "\n[timeout]",
        }
    except FileNotFoundError:
        return {
            "cmd": cmd,
            "returncode": None,
            "stdout": "",
            "stderr": "command not found",
        }

