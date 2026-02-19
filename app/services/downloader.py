from pathlib import Path
import json
import time
import requests
from app.services.storage import ensure_dirs

def download_images(items, folder: str = "images"):
    base = ensure_dirs()
    out_dir = base / "images" / folder
    out_dir.mkdir(parents=True, exist_ok=True)

    meta = []
    for it in items:
        url = it["image_url"] if isinstance(it, dict) else it.image_url
        provider = it["provider"] if isinstance(it, dict) else it.provider
        img_id = it["id"] if isinstance(it, dict) else it.id

        filename = f"{provider}_{img_id}.jpg"
        path = out_dir / filename

        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        path.write_bytes(resp.content)

        meta.append({
            "saved_path": str(path).replace("\\", "/"),
            "downloaded_at": int(time.time()),
            "provider": provider,
            "id": img_id,
            "source": (it["page_url"] if isinstance(it, dict) else it.page_url),
        })

    meta_path = out_dir / "metadata.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    return {"count": len(meta), "folder": str(out_dir).replace("\\", "/"), "metadata": str(meta_path).replace("\\", "/")}
