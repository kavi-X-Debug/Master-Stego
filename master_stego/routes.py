import uuid
import os
from flask import Blueprint, render_template, request, jsonify, send_from_directory, abort

from master_stego import TMP_DIR
from master_stego.analysis.pipeline import run_full_analysis


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

    app.register_blueprint(bp)

