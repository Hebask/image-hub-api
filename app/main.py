from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.api.routes import router as main_router
from app.api.routes_datasets import router as datasets_router
from app.api.routes_datasets_download import router as datasets_download_router

app = FastAPI()

app.include_router(main_router)
app.include_router(datasets_router)
app.include_router(datasets_download_router)
