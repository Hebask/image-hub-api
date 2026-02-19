from pathlib import Path
import json
import time
import mimetypes
import requests
from app.services.storage import ensure_dirs
from app.services.dedup import sha256_file, load_hash_index, save_hash_index

def _guess_ext(content_type: str | None, fallback: str = ".jpg") -> str:
    if not content_type:
        return fallback
    content_type = content_type.split(";")[0].strip().lower()
    ext = mimetypes.guess_extension(content_type)
    return ext if ext else fallback


def download_images(items, folder: str = "images"):
    base = ensure_dirs()
    out_dir = Path(base) / "images" / folder
    out_dir.mkdir(parents=True, exist_ok=True)
    known_hashes = load_hash_index(out_dir)
    skipped = 0

    meta = []
    for it in items:
        provider = it["provider"] if isinstance(it, dict) else it.provider
        img_id = it["id"] if isinstance(it, dict) else it.id
        url = it["image_url"] if isinstance(it, dict) else it.image_url
        page_url = it["page_url"] if isinstance(it, dict) else it.page_url

        resp = requests.get(url, stream=True, timeout=60)
        resp.raise_for_status()

        ext = _guess_ext(resp.headers.get("content-type"), ".jpg")
        filename = f"{provider}_{img_id}{ext}"
        path = out_dir / filename

        with open(path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 256):
                if chunk:
                    f.write(chunk)
        
        file_hash = sha256_file(path)
        if file_hash in known_hashes:
            # duplicate found → delete and skip
            path.unlink(missing_ok=True)
            skipped += 1
            continue

        known_hashes.add(file_hash)


        meta.append({
            "saved_path": str(path).replace("\\", "/"),
            "downloaded_at": int(time.time()),
            "provider": provider,
            "id": img_id,
            "source_page": page_url,
            "image_url": url,
            "content_type": resp.headers.get("content-type"),
        })

    meta_path = out_dir / "metadata.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    save_hash_index(out_dir, known_hashes)

    return {
    "count": len(meta),
    "skipped_duplicates": skipped,
    "folder": str(out_dir).replace("\\", "/"),
    "metadata": str(meta_path).replace("\\", "/"),
    "files": [m["saved_path"] for m in meta],
    }


