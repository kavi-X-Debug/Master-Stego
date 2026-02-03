
# Master Stego

Master Stego is a CTF-focused image steganography analysis web application inspired by AperiSolve. It is designed as a single-click workbench for common image stego techniques used in Capture-The-Flag challenges.

## Features

- Image upload for PNG, JPG/JPEG, BMP
- Automatic analysis pipeline:
  - File information (format, size, resolution, hashes)
  - EXIF metadata extraction (Pillow and exiftool)
  - Strings extraction (ASCII and UTF-16 via strings)
  - Header/footer validation and signature checks
  - Binwalk scan with auto-extraction of embedded files
  - Color channel separation (R, G, B, Alpha)
  - Image enhancements (invert, contrast, threshold)
  - Bit-plane slicing for all channels and bits 0–7
  - LSB extraction (per-channel and combined)
  - zsteg analysis for PNG
  - steghide info and extraction attempts (empty password)
  - OutGuess/OpenStego detection and extraction attempts (if installed)
  - Embedded compression detection (ZIP, ZLIB, GZIP)
  - Encoding detection (Base64, hex, binary, ROT13)
- Automatic flag detection using regex patterns:
  - `flag{...}`
  - `ctf{...}`
  - `genzipher{...}`
- Dark, terminal-like UI with per-module tabs and image preview panels

## Tech Stack

- Backend: Python, Flask
- Frontend: HTML, TailwindCSS (CDN), JavaScript
- Image processing: Pillow, OpenCV, NumPy
- External tools (CLI, assumed installed in PATH on Linux):
  - exiftool
  - binwalk
  - zsteg
  - steghide
  - strings
  - (optional) outguess, openstego

## Project Structure

High-level layout:

- `app.py` – Flask application entrypoint
- `master_stego/`
  - `__init__.py` – package setup and temp directory
  - `routes.py` – HTTP routes and upload handling
  - `analysis/` – modular analysis components
  - `utils/` – helper utilities (subprocess handling, etc.)
- `templates/index.html` – main UI
- `static/js/main.js` – frontend logic
- `requirements.txt` – Python dependencies

## Running Locally

Requirements:

- Python 3.10+
- Linux system with the following tools installed and available in `PATH`:
  - `exiftool`
  - `strings`
  - `binwalk`
  - `zsteg`
  - `steghide`


### Setup

```bash
cd master_stego
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Run the server

```bash
export FLASK_APP=app:app
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

Then open http://localhost:5000 in your browser.

Temporary analysis artifacts are stored under `master_stego/master_stego/tmp/` and are grouped by random session IDs per upload.

## Security and Legal Disclaimer

- Master Stego is intended exclusively for educational use and CTF practice.
- Do not use this tool on data you do not own or do not have explicit permission to analyze.
- The authors and operators of this tool are not responsible for misuse or any resulting damage.

## Deploying to Render / Railway

### Common configuration

- Python runtime: 3.10+
- Start command:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

- Set `PYTHONUNBUFFERED=1` for better logging.
- Ensure the following system packages are installed (via buildpacks or Docker base image):
  - `exiftool`
  - `binwalk`
  - `strings` (usually from `binutils` or similar package)
  - `steghide`
  - `zsteg` (often via Ruby gems) and any of its OS-level dependencies
  - optional: `outguess`, `openstego`

You will typically do this by using a custom Dockerfile or a platform configuration that installs additional packages during build.

### Render Notes

- Use a Web Service pointing to this repository root.
- Set the build command to:

```bash
pip install -r requirements.txt
```

- Set the start command to the `gunicorn` command above.
- If using a Docker deploy, define all system packages in your `Dockerfile`.

### Railway Notes

- Create a new Python service from this repository.
- In the service settings:
  - Set the install command to `pip install -r requirements.txt`.
  - Set the start command to the `gunicorn` command above.
- For advanced setups, define a `Dockerfile` at the repo root and configure system packages there.



- This project does not implement authentication; do not expose it to untrusted networks without additional hardening.
- CPU and memory usage depend on the size of uploaded images and the behavior of external CLI tools (e.g., `binwalk`, `zsteg`).

>>>>>>> 9f72f47 (Initial Commit)
