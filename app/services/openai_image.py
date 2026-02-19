import base64
from pathlib import Path
from openai import OpenAI
from app.core.config import settings
from app.services.storage import ensure_dirs

def generate_image(prompt: str, size: str = "1024x1024"):
    if not settings.openai_api_key or "YOUR_" in settings.openai_api_key:
        raise RuntimeError("Missing OPENAI_API_KEY in .env")

    client = OpenAI(api_key=settings.openai_api_key)
    base = ensure_dirs()
    out_dir = Path(settings.storage_dir) / "images" / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)

    result = client.images.generate(
        model=settings.openai_image_model,
        prompt=prompt,
        size=size,
    )

    img = result.data[0]
    if getattr(img, "b64_json", None):
        data = base64.b64decode(img.b64_json)
        path = out_dir / "generated.png"
        path.write_bytes(data)
        return {"saved_path": str(path).replace("\\", "/")}
    elif getattr(img, "url", None):
        return {"url": img.url}
    else:
        return {"result": "No image returned (unexpected format)"}
