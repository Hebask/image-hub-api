# Image Hub API (FastAPI)

## Run
```bash
uvicorn app.main:app --reload

## Open Swagger: 
    http://127.0.0.1:8000/docs

##Endpoints

GET /search?q=...&provider=unsplash

POST /download

POST /edit

POST /vision/ask

POST /image/generate


---

# Run it

```bash
uvicorn app.main:app --reload

#Then go to:

http://127.0.0.1:8000/docs