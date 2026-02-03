import os

from master_stego.analysis import (
    file_info,
    exif_metadata,
    strings_analysis,
    header_footer,
    binwalk_analysis,
    color_channels,
    enhancements,
    bitplanes,
    lsb_analysis,
    zsteg_module,
    steghide_module,
    outguess_openstego,
    compression_detection,
    encoding_detection,
    flag_detection,
)


def run_full_analysis(file_path, session_id, session_dir):
    result = {
        "session_id": session_id,
        "file_info": {},
        "exif": {},
        "strings": {},
        "header_footer": {},
        "binwalk": {},
        "color_channels": {},
        "enhancements": {},
        "bitplanes": {},
        "lsb": {},
        "zsteg": {},
        "steghide": {},
        "encodings": {},
        "flags": {},
        "extracted_files": [],
    }

    def safe_run(name, func):
        try:
            return func()
        except Exception as exc:
            return {"error": str(exc), "module": name}

    result["file_info"] = safe_run("file_info", lambda: file_info.analyze(file_path))
    result["exif"] = safe_run("exif", lambda: exif_metadata.analyze(file_path))
    result["strings"] = safe_run("strings", lambda: strings_analysis.analyze(file_path))
    result["header_footer"] = safe_run("header_footer", lambda: header_footer.analyze(file_path))
    result["binwalk"] = safe_run("binwalk", lambda: binwalk_analysis.analyze(file_path, session_dir))
    result["color_channels"] = safe_run(
        "color_channels", lambda: color_channels.analyze(file_path, session_id, session_dir)
    )
    result["enhancements"] = safe_run(
        "enhancements", lambda: enhancements.analyze(file_path, session_id, session_dir)
    )
    result["bitplanes"] = safe_run("bitplanes", lambda: bitplanes.analyze(file_path, session_id, session_dir))
    result["lsb"] = safe_run("lsb", lambda: lsb_analysis.analyze(file_path))

    _, ext = os.path.splitext(file_path.lower())
    if ext == ".png":
        result["zsteg"] = safe_run("zsteg", lambda: zsteg_module.analyze(file_path))
    else:
        result["zsteg"] = {"skipped": True, "reason": "zsteg is PNG-only"}

    result["steghide"] = safe_run("steghide", lambda: steghide_module.analyze(file_path, session_dir))
    result["encodings"] = safe_run("encodings", lambda: encoding_detection.analyze(result["strings"]))
    result["flags"] = safe_run("flags", lambda: flag_detection.analyze(result))

    extracted = []
    for root, _, files in os.walk(session_dir):
        for f in files:
            rel_path = os.path.relpath(os.path.join(root, f), session_dir)
            extracted.append(
                {
                    "name": rel_path,
                    "url": f"/api/session/{session_id}/files/{rel_path.replace(os.sep, '/')}",
                }
            )
    result["extracted_files"] = extracted

    return result
