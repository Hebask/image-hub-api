from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.core.config import settings

router = APIRouter(prefix="/datasets", tags=["datasets"])

@router.get("/download")
def download_zip(zip_name: str):
    zip_path = Path(settings.storage_dir) / "exports" / zip_name
    if not zip_path.exists():
        raise HTTPException(status_code=404, detail=f"ZIP not found: {zip_name}")

    return FileResponse(
        path=str(zip_path),
        media_type="application/zip",
        filename=zip_name,
    )
