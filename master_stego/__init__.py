import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = os.path.join(BASE_DIR, "tmp")

os.makedirs(TMP_DIR, exist_ok=True)

