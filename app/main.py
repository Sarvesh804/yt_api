from fastapi import FastAPI, Query
from contextlib import asynccontextmanager
from .db import database, metadata, engine
from .models import videos
from .tasks import fetch_latest_videos
from typing import List, Optional
from .schemas import VideoOut
import asyncio


metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    fetcher_task = asyncio.create_task(run_fetcher())  
    try:
        yield
    finally:
        fetcher_task.cancel()  
        await database.disconnect()


async def run_fetcher():
    while True:
        await fetch_latest_videos()
        await asyncio.sleep(10)


app = FastAPI(
    title="Youtube Video Fetcher API",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "API is running!"}


@app.get("/videos", response_model=List[VideoOut])
async def get_videos(
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0)
):
    query = videos.select().order_by(videos.c.published_at.desc()).limit(limit).offset(offset)
    results = await database.fetch_all(query)
    return results
