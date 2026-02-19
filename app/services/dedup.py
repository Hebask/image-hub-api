from pathlib import Path
import hashlib

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def load_hash_index(folder: Path) -> set[str]:
    index_file = folder / ".hash_index.txt"
    if not index_file.exists():
        return set()
    return set(x.strip() for x in index_file.read_text(encoding="utf-8").splitlines() if x.strip())

def save_hash_index(folder: Path, hashes: set[str]) -> None:
    index_file = folder / ".hash_index.txt"
    index_file.write_text("\n".join(sorted(hashes)), encoding="utf-8")
