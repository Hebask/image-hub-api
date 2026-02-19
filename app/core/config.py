from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    storage_dir: str = os.getenv("STORAGE_DIR", "storage")

    unsplash_access_key: str | None = os.getenv("UNSPLASH_ACCESS_KEY")

    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_vision_model: str = os.getenv("OPENAI_VISION_MODEL", "gpt-4.1-mini")
    openai_image_model: str = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")

    bing_api_key: str | None = os.getenv("BING_API_KEY")
    bing_endpoint: str = os.getenv("BING_ENDPOINT", "https://api.bing.microsoft.com/v7.0/images/search")


settings = Settings()
