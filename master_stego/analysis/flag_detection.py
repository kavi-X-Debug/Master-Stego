import re
from typing import Dict, Any, List


FLAG_PATTERNS = [
    re.compile(r"flag\{.*?\}", re.IGNORECASE),
    re.compile(r"ctf\{.*?\}", re.IGNORECASE),
    re.compile(r"genzipher\{.*?\}", re.IGNORECASE),
]


def analyze(full_result: Dict[str, Any]) -> Dict[str, Any]:
    found: List[Dict[str, Any]] = []

    def scan_text(text: str, source: str):
        if not text:
            return
        for pattern in FLAG_PATTERNS:
            for match in pattern.findall(text):
                found.append({"flag": match, "source": source})

    file_info = full_result.get("file_info") or {}
    for key, value in file_info.items():
        if isinstance(value, str):
            scan_text(value, f"file_info.{key}")

    exif = full_result.get("exif") or {}
    for tool_name, data in exif.items():
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    scan_text(value, f"exif.{tool_name}.{key}")

    strings_res = full_result.get("strings") or {}
    for key in ("ascii", "utf16"):
        section = strings_res.get(key) or {}
        sample = section.get("sample") or []
        for line in sample:
            scan_text(line, f"strings.{key}")

    binwalk_res = full_result.get("binwalk") or {}
    if isinstance(binwalk_res.get("summary"), str):
        scan_text(binwalk_res["summary"], "binwalk.summary")

    zsteg_res = full_result.get("zsteg") or {}
    if isinstance(zsteg_res.get("stdout"), str):
        scan_text(zsteg_res["stdout"], "zsteg.stdout")

    steghide_res = full_result.get("steghide") or {}
    for section_name in ("info", "extract"):
        section = steghide_res.get(section_name) or {}
        for key in ("stdout", "stderr"):
            if isinstance(section.get(key), str):
                scan_text(section[key], f"steghide.{section_name}.{key}")

    encodings = full_result.get("encodings") or {}
    for enc_type, entries in encodings.items():
        if isinstance(entries, list):
            for entry in entries:
                decoded = entry.get("decoded")
                if isinstance(decoded, str):
                    scan_text(decoded, f"encodings.{enc_type}")

    lsb = full_result.get("lsb") or {}
    for section_name, section in lsb.items():
        if isinstance(section, dict):
            preview = section.get("preview")
            if isinstance(preview, str):
                scan_text(preview, f"lsb.{section_name}")
        elif isinstance(section, str):
            scan_text(section, f"lsb.{section_name}")

    return {"count": len(found), "flags": found}

