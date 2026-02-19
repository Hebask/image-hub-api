import os
import io
from typing import Optional

from openai import OpenAI
from fastapi import HTTPException


def _get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY is not set. Set it in your environment or .env to use OpenAI features.",
        )
    return OpenAI(api_key=api_key)


def edit_image_bytes(
    image_bytes: bytes,
    prompt: str,
    *,
    size: str = "1024x1024",
    model: Optional[str] = None,
) -> bytes:
    client = _get_client()
    model = model or os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")

    try:
        image_file = io.BytesIO(image_bytes)
        image_file.name = "image.png"

        result = client.images.edits(
            model=model,
            image=image_file,
            prompt=prompt,
            size=size,
        )

        b64 = result.data[0].b64_json
        import base64

        return base64.b64decode(b64)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI edit failed: {e}")
