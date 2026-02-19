from pathlib import Path
import zipfile
from app.core.config import settings
from app.services.storage import ensure_dirs

def export_folder_as_zip(folder: str, zip_name: str = "dataset.zip") -> str:
    ensure_dirs()

    images_dir = Path(settings.storage_dir) / "images" / folder
    if not images_dir.exists():
        raise FileNotFoundError(f"Folder not found: {images_dir}")

    exports_dir = Path(settings.storage_dir) / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)

    out_zip = exports_dir / zip_name

    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in images_dir.rglob("*"):
            if p.is_file():
                arcname = Path(folder) / p.name
                z.write(p, arcname=str(arcname))

    return str(out_zip).replace("\\", "/")
