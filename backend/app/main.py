from fastapi import FastAPI

from app.routers import auth, episodes, words

app = FastAPI(title="SubLingo API", version="0.1.0")
app.include_router(auth.router)
app.include_router(episodes.router)
app.include_router(words.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}