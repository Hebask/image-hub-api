import os
import base64
from typing import Optional
from fastapi import HTTPException
from openai import OpenAI


def _get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY is not set. Set it in your environment or .env to use OpenAI features.",
        )
    return OpenAI(api_key=api_key)


def generate_image_bytes(
    prompt: str,
    *,
    size: str = "1024x1024",
    model: Optional[str] = None,
) -> bytes:
    client = _get_client()
    model = model or os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")

    try:
        result = client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
        )
        return base64.b64decode(result.data[0].b64_json)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI generate failed: {e}")
