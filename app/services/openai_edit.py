import os
import base64
from io import BytesIO
from pathlib import Path
from typing import Optional
from PIL import Image
from openai import OpenAI

def _client() -> OpenAI:
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

client = _client()

def _to_png_rgba_bytes(image_path: str) -> bytes:
    p = Path(image_path)
    if not p.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    with Image.open(p) as img:
        img = img.convert("RGBA")
        buf = BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

def _full_transparent_mask_bytes(image_path: str) -> bytes:
    with Image.open(image_path) as img:
        w, h = img.size
    mask = Image.new("RGBA", (w, h), (0, 0, 0, 0)) 
    buf = BytesIO()
    mask.save(buf, format="PNG")
    return buf.getvalue()

def _read_mask_png_bytes(mask_path: str, image_path: str) -> bytes:
    mp = Path(mask_path)
    if not mp.exists():
        raise FileNotFoundError(f"Mask not found: {mask_path}")
    with Image.open(image_path) as base:
        w, h = base.size
    with Image.open(mp) as m:
        m = m.convert("RGBA").resize((w, h))
        buf = BytesIO()
        m.save(buf, format="PNG")
        return buf.getvalue()

def edit_image_bytes(image_path: str, instruction: str, mask_path: Optional[str] = None) -> bytes:
    model = os.getenv("OPENAI_IMAGE_MODEL", "dall-e-2")
    size = os.getenv("OPENAI_IMAGE_SIZE", "1024x1024")

    image_png = _to_png_rgba_bytes(image_path)

    if mask_path:
        mask_png = _read_mask_png_bytes(mask_path, image_path)
    else:
        mask_png = _full_transparent_mask_bytes(image_path)

    res = client.images.edit(
        model=model,
        image=("image.png", image_png, "image/png"),
        mask=("mask.png", mask_png, "image/png"),
        prompt=instruction,
        size=size,
        response_format="b64_json",
    )

    b64 = res.data[0].b64_json
    if not b64:
        raise RuntimeError(f"No b64 returned. data0={res.data[0]}")
    return base64.b64decode(b64)
