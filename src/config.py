from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_RAW = BASE_DIR / "data/raw"
DATA_PROCESSED = BASE_DIR / "data/processed"
OUTPUTS = BASE_DIR / "outputs"