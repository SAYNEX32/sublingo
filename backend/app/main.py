from fastapi import FastAPI

from app.routers import episodes

app = FastAPI(title="SubLingo API", version="0.1.0")
app.include_router(episodes.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}