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
        "outguess_openstego": {},
        "compression": {},
        "encodings": {},
        "flags": {},
        "extracted_files": [],
    }

    result["file_info"] = file_info.analyze(file_path)
    result["exif"] = exif_metadata.analyze(file_path)
    result["strings"] = strings_analysis.analyze(file_path)
    result["header_footer"] = header_footer.analyze(file_path)
    result["binwalk"] = binwalk_analysis.analyze(file_path, session_dir)
    result["color_channels"] = color_channels.analyze(file_path, session_id, session_dir)
    result["enhancements"] = enhancements.analyze(file_path, session_id, session_dir)
    result["bitplanes"] = bitplanes.analyze(file_path, session_id, session_dir)
    result["lsb"] = lsb_analysis.analyze(file_path)

    _, ext = os.path.splitext(file_path.lower())
    if ext == ".png":
        result["zsteg"] = zsteg_module.analyze(file_path)
    else:
        result["zsteg"] = {"skipped": True, "reason": "zsteg is PNG-only"}

    result["steghide"] = steghide_module.analyze(file_path, session_dir)
    result["outguess_openstego"] = outguess_openstego.analyze(file_path, session_dir)
    result["compression"] = compression_detection.analyze(file_path)
    result["encodings"] = encoding_detection.analyze(result["strings"])
    result["flags"] = flag_detection.analyze(result)

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
