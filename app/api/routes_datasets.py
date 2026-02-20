from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.dataset_export import export_folder_as_zip

router = APIRouter(prefix="/datasets", tags=["datasets"])

class ExportRequest(BaseModel):
    folder: str  
    zip_name: str = "dataset.zip"

@router.post("/export")
def export_dataset(req: ExportRequest):
    try:
        out_path = export_folder_as_zip(folder=req.folder, zip_name=req.zip_name)
        return {"zip_path": out_path}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
