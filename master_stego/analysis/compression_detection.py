from typing import Dict, Any, List


def analyze(file_path: str) -> Dict[str, Any]:
    try:
        with open(file_path, "rb") as f:
            data = f.read()
    except Exception as exc:
        return {"error": str(exc)}

    findings: List[Dict[str, Any]] = []

    magic_signatures = [
        ("zip", b"\x50\x4b\x03\x04"),
        ("gzip", b"\x1f\x8b"),
        ("zlib", b"\x78\x9c"),
        ("zlib", b"\x78\x01"),
        ("zlib", b"\x78\xda"),
    ]

    for name, sig in magic_signatures:
        offset = 0
        while True:
            idx = data.find(sig, offset)
            if idx == -1:
                break
            findings.append({"type": name, "offset": idx})
            offset = idx + 1

    return {"findings": findings}

