import requests
from fastapi import HTTPException
from app.core.config import settings

class UnsplashProvider:
    BASE = "https://api.unsplash.com"

    def search(self, q: str, limit: int = 24):
        if not settings.unsplash_access_key or "YOUR_" in settings.unsplash_access_key:
            raise HTTPException(500, "Missing UNSPLASH_ACCESS_KEY in .env")

        r = requests.get(
            f"{self.BASE}/search/photos",
            params={"query": q, "per_page": min(limit, 30)},
            headers={"Authorization": f"Client-ID {settings.unsplash_access_key}"},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()

        out = []
        for item in data.get("results", []):
            out.append({
                "provider": "unsplash",
                "id": item["id"],
                "page_url": item["links"]["html"],
                "image_url": item["urls"]["raw"],
                "thumb_url": item["urls"]["thumb"],
                "width": item["width"],
                "height": item["height"],
                "author": item["user"]["name"],
                "license": "Unsplash license (check source page)"
            })
        return out
