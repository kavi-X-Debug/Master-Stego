import uuid
import os
import json
import urllib.request
import urllib.error
from flask import Blueprint, render_template, request, jsonify, send_from_directory, abort

from master_stego import TMP_DIR
from master_stego.analysis.pipeline import run_full_analysis


def _call_gemini(api_key, analysis, message):
    url = (
        "https://generativelanguage.googleapis.com/v1/models/"
        "gemini-1.5-flash-001:generateContent?key=" + api_key
    )

    context_text = (
        "You are a CTF steganography assistant. The user has run a suite of tools "
        "on an image to search for hidden data and flags. "
        "Use the JSON analysis output and the user question to give concise, "
        "practical guidance for finding or validating flags.\n\n"
        "Analysis JSON:\n"
        + json.dumps(analysis, default=str) +
        "\n\nUser question:\n" +
        message
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": context_text,
                    }
                ]
            }
        ]
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp_data = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8")
        except Exception:
            body = ""
        return None, f"Gemini API HTTP error: {exc.code} {exc.reason} {body}"
    except urllib.error.URLError as exc:
        return None, f"Gemini API connection error: {exc.reason}"
    except Exception as exc:
        return None, f"Gemini API request failed: {exc}"

    try:
        parsed = json.loads(resp_data)
    except Exception:
        return None, "Failed to parse Gemini response JSON"

    try:
        candidates = parsed.get("candidates") or []
        if not candidates:
            return None, "Empty response from Gemini"
        content = candidates[0].get("content") or {}
        parts = content.get("parts") or []
        texts = [p.get("text") for p in parts if isinstance(p.get("text"), str)]
        if not texts:
            return None, "No text in Gemini response"
        return "\n\n".join(texts), None
    except Exception as exc:
        return None, f"Unexpected Gemini response format: {exc}"


def register_routes(app):
    bp = Blueprint("master_stego", __name__)

    @bp.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    @bp.route("/favicon.ico", methods=["GET"])
    def favicon():
        return send_from_directory(app.root_path, "fav.png", mimetype="image/png")

    @bp.route("/api/analyze", methods=["POST"])
    def analyze():
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        uploaded = request.files["file"]
        if uploaded.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        ext = os.path.splitext(uploaded.filename.lower())[1]
        if ext not in [".png", ".jpg", ".jpeg", ".bmp"]:
            return jsonify({"error": "Unsupported file type"}), 400

        session_id = uuid.uuid4().hex
        session_dir = os.path.join(TMP_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)

        filename = "input" + ext
        file_path = os.path.join(session_dir, filename)
        uploaded.save(file_path)

        result = run_full_analysis(file_path=file_path, session_id=session_id, session_dir=session_dir)

        return jsonify(result)

    @bp.route("/api/session/<session_id>/files/<path:filename>", methods=["GET"])
    def download_file(session_id, filename):
        if not session_id.isalnum():
            abort(404)

        session_dir = os.path.join(TMP_DIR, session_id)
        session_dir = os.path.abspath(session_dir)
        tmp_dir_abs = os.path.abspath(TMP_DIR)

        if not session_dir.startswith(tmp_dir_abs):
            abort(404)

        if not os.path.isdir(session_dir):
            abort(404)

        return send_from_directory(session_dir, filename, as_attachment=True)

    @bp.route("/api/chat", methods=["POST"])
    def chat():
        data = request.get_json(silent=True) or {}
        message = str(data.get("message", "")).strip()
        if not message:
            return jsonify({"error": "Message is required"}), 400

        analysis = data.get("analysis") or {}

        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            return jsonify({"error": "Gemini API key not configured on server"}), 500

        reply, error = _call_gemini(api_key, analysis, message)
        if error:
            return jsonify({"error": error}), 502

        return jsonify({"reply": reply})

    app.register_blueprint(bp)

