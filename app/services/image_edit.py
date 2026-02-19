from PIL import Image
from pathlib import Path

def edit_image(image_path: str, action: str, width=None, height=None, degrees=None,
               format=None, crop_box=None, quality=None):
    p = Path(image_path)
    if not p.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    img = Image.open(p)

    if action == "resize":
        if not width or not height:
            raise ValueError("width and height required for resize")
        img = img.resize((int(width), int(height)))

    elif action == "rotate":
        if degrees is None:
            raise ValueError("degrees required for rotate")
        img = img.rotate(int(degrees), expand=True)

    elif action == "crop":
        if not crop_box or len(crop_box) != 4:
            raise ValueError("crop_box [left, top, right, bottom] required")
        img = img.crop(tuple(map(int, crop_box)))

    elif action == "convert":
        if format is None:
            raise ValueError("format required for convert (JPEG/PNG/WEBP)")

    elif action == "compress":
        pass

    else:
        raise ValueError("Unknown action")

    out_format = format if format else (img.format or "JPEG")
    out_path = p.with_name(p.stem + f"_edited.{out_format.lower()}")

    save_kwargs = {}
    if quality is not None:
        save_kwargs["quality"] = int(quality)

    img.save(out_path, out_format, **save_kwargs)
    return str(out_path).replace("\\", "/")
