from pathlib import Path
from PIL import Image

IMG_PATH = Path("storage/images/recreated/unsplash_7GX5aICb514_recreated.png")
MASK_PATH = Path("storage/masks/bandana_mask.png")

MASK_PATH.parent.mkdir(parents=True, exist_ok=True)

img = Image.open(IMG_PATH).convert("RGBA")
w, h = img.size

mask = Image.new("RGBA", (w, h), (255, 255, 255, 255))
mask.save(MASK_PATH, "PNG")

print("Saved:", MASK_PATH, "size:", (w, h))
