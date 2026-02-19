from pathlib import Path
from app.core.config import settings

def ensure_dirs():
    base = Path(settings.storage_dir)
    (base / "images").mkdir(parents=True, exist_ok=True)
    (base / "exports").mkdir(parents=True, exist_ok=True)
    return base
