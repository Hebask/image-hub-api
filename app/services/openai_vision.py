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


def ask_about_image(
    image_bytes: bytes,
    question: str,
    *,
    model: Optional[str] = None,
) -> str:
    client = _get_client()
    model = model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    try:
        b64 = base64.b64encode(image_bytes).decode("utf-8")

        resp = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{b64}"},
                        },
                    ],
                }
            ],
        )

        return resp.choices[0].message.content or ""

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI vision failed: {e}")
