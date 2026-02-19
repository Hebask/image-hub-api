from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, List, Optional

from app.providers.unsplash import UnsplashProvider
from app.services.downloader import download_images
from app.services.image_edit import edit_image
from app.services.openai_vision import ask_about_image
from app.services.openai_image import generate_image

router = APIRouter()

ProviderName = Literal["unsplash"]

class SearchResponseItem(BaseModel):
    provider: str
    id: str
    page_url: str
    image_url: str
    thumb_url: str
    width: int
    height: int
    author: Optional[str] = None
    license: Optional[str] = None

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/search", response_model=List[SearchResponseItem])
def search(q: str, provider: ProviderName = "unsplash", limit: int = 24):
    if provider == "unsplash":
        p = UnsplashProvider()
        return p.search(q=q, limit=limit)
    raise HTTPException(400, "Unknown provider")

class DownloadRequest(BaseModel):
    items: List[SearchResponseItem]
    folder: str = Field(default="images", description="Subfolder under storage/images")

@router.post("/download")
def download(req: DownloadRequest):
    result = download_images(req.items, folder=req.folder)
    return result

class EditRequest(BaseModel):
    image_path: str
    action: Literal["resize","rotate","convert","crop","compress"]
    width: Optional[int] = None
    height: Optional[int] = None
    degrees: Optional[int] = None
    format: Optional[Literal["JPEG","PNG","WEBP"]] = None
    crop_box: Optional[List[int]] = None  # [left, top, right, bottom]
    quality: Optional[int] = None  # 1-95

@router.post("/edit")
def edit(req: EditRequest):
    out = edit_image(**req.model_dump())
    return {"output_path": out}

class VisionAskRequest(BaseModel):
    image_path: str
    question: str

@router.post("/vision/ask")
def vision_ask(req: VisionAskRequest):
    answer = ask_about_image(image_path=req.image_path, question=req.question)
    return {"answer": answer}

class GenerateRequest(BaseModel):
    prompt: str
    size: Optional[str] = "1024x1024"

@router.post("/image/generate")
def image_generate(req: GenerateRequest):
    out = generate_image(prompt=req.prompt, size=req.size)
    return out
