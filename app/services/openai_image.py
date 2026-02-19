import base64
import os
from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_image_bytes(prompt: str) -> bytes:
    model = getattr(settings, "openai_image_model", None) or os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")

    res = client.images.generate(
        model=model,
        prompt=prompt,
        size="1024x1024"
    )

    # OpenAI returns base64 image data
    b64 = res.data[0].b64_json
    return base64.b64decode(b64)
