from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, List, Optional
from app.services.openai_edit import edit_image_bytes
from app.providers.unsplash import UnsplashProvider
from app.services.downloader import download_images
from app.services.image_edit import edit_image
from app.services.openai_vision import ask_about_image
from app.services.openai_image import generate_image_bytes
from app.services.storage import ensure_dirs
from app.core.config import settings
from app.services.storage import ensure_dirs
from pathlib import Path
import json
import base64

router = APIRouter()

ProviderName = Literal["unsplash"]

class RecreateFromDatasetRequest(BaseModel):
    folder: str                 
    index: int = 0             
    out_folder: str = "recreated"
    out_filename: str | None = None
    prompt_prefix: str = "Photorealistic, high quality, soft lighting. "

class ImageGenerateRequest(BaseModel):
    prompt: str
    folder: str = "generated"
    filename: str = "generated.png"

class VisionBatchRequest(BaseModel):
    folder: str
    question: str = "Describe the image in one sentence."

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

class ImageEditRequest(BaseModel):
    image_path: str
    instruction: str
    out_folder: str = "edited"
    out_filename: str = "edited.png"
    mask_path: Optional[str] = None  

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/image/generate")
def image_generate(req: ImageGenerateRequest):
    ensure_dirs()
    out_dir = Path(settings.storage_dir) / "images" / req.folder
    out_dir.mkdir(parents=True, exist_ok=True)

    img_bytes = generate_image_bytes(prompt=req.prompt)

    out_path = out_dir / req.filename
    out_path.write_bytes(img_bytes)

    return {"saved_path": str(out_path).replace("\\", "/")}

@router.post("/vision/batch")
def vision_batch(req: VisionBatchRequest):
    folder_path = Path(settings.storage_dir) / "images" / req.folder
    if not folder_path.exists():
        raise HTTPException(404, f"Folder not found: {req.folder}")

    meta_path = folder_path / "metadata.json"
    if not meta_path.exists():
        raise HTTPException(404, f"metadata.json not found in {req.folder}")

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    updated = 0

    for item in meta:
        img_path = item.get("saved_path")
        if not img_path:
            continue

        # skip if already answered for this same question
        qa = item.get("vision_qa", [])
        if any(x.get("q") == req.question for x in qa):
            continue

        ans = ask_about_image(image_path=img_path, question=req.question)

        qa.append({"q": req.question, "a": ans})
        item["vision_qa"] = qa
        updated += 1

    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return {"folder": req.folder, "updated": updated, "metadata": str(meta_path).replace("\\", "/")}

@router.get("/search", response_model=List[SearchResponseItem])
def search(q: str, provider: ProviderName = "unsplash", limit: int = 24):
    q = q.replace("q=", "").split("&")[0].strip()
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
    out = generate_image_bytes(prompt=req.prompt, size=req.size)
    return out


@router.post("/image/recreate-from-dataset")
def recreate_from_dataset(req: RecreateFromDatasetRequest):
    ensure_dirs()

    folder_path = Path(settings.storage_dir) / "images" / req.folder
    meta_path = folder_path / "metadata.json"
    if not meta_path.exists():
        raise HTTPException(404, f"metadata.json not found in {req.folder}")

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if req.index < 0 or req.index >= len(meta):
        raise HTTPException(400, f"index out of range. max index = {len(meta)-1}")

    item = meta[req.index]
    qa = item.get("vision_qa", [])
    if not qa:
        raise HTTPException(400, "No vision_qa found. Run POST /vision/batch first.")

    # take last answer as caption/prompt base
    caption = qa[-1].get("a") or ""
    if not caption.strip():
        raise HTTPException(400, "No caption answer found in vision_qa.")

    prompt = req.prompt_prefix + caption

    out_dir = Path(settings.storage_dir) / "images" / req.out_folder
    out_dir.mkdir(parents=True, exist_ok=True)

    # default filename: provider_id_recreated.png
    default_name = f"{item.get('provider','img')}_{item.get('id','item')}_recreated.png"
    filename = req.out_filename or default_name
    out_path = out_dir / filename

    img_bytes = generate_image_bytes(prompt=prompt)
    out_path.write_bytes(img_bytes)

    # write back into metadata
    item["recreated_path"] = str(out_path).replace("\\", "/")
    item["recreated_prompt"] = prompt
    meta[req.index] = item
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    return {
        "index": req.index,
        "prompt": prompt,
        "saved_path": str(out_path).replace("\\", "/"),
        "metadata": str(meta_path).replace("\\", "/"),
    }

@router.post("/image/edit")
def image_edit(req: ImageEditRequest):
    out_dir = Path(settings.storage_dir) / "images" / req.out_folder
    out_dir.mkdir(parents=True, exist_ok=True)

    edited = edit_image_bytes(
        image_path=req.image_path,
        instruction=req.instruction,
        mask_path=req.mask_path
    )

    out_path = out_dir / req.out_filename
    out_path.write_bytes(edited)

    return {"saved_path": str(out_path).replace("\\", "/")}