import base64
from pathlib import Path
from openai import OpenAI
from app.core.config import settings

def _to_data_url(image_path: str) -> str:
    p = Path(image_path)
    b = p.read_bytes()
    ext = p.suffix.lower().lstrip(".")
    mime = "jpeg" if ext in ["jpg","jpeg"] else ext
    return f"data:image/{mime};base64," + base64.b64encode(b).decode("utf-8")

def ask_about_image(image_path: str, question: str) -> str:
    if not settings.openai_api_key or "YOUR_" in settings.openai_api_key:
        raise RuntimeError("Missing OPENAI_API_KEY in .env")

    client = OpenAI(api_key=settings.openai_api_key)

    resp = client.responses.create(
        model=settings.openai_vision_model,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": question},
                    {"type": "input_image", "image_url": _to_data_url(image_path)},
                ],
            }
        ],
    )
    return resp.output_text
