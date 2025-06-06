from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from .db import database, metadata, engine
from .models import videos
from .tasks import fetch_latest_videos
from typing import List, Optional
from sqlalchemy import and_, or_, desc, asc
from .schemas import VideoOut
import asyncio, httpx
from datetime import datetime


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
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "API is running!"}


@app.get("/videos", response_model=List[VideoOut])
async def get_videos(
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    title: Optional[str] = Query(None, description="Partial match for video title"),
    description: Optional[str] = Query(None, description="Partial match for description"),
    published_after: Optional[datetime] = Query(None, description="Published after this datetime"),
    published_before: Optional[datetime] = Query(None, description="Published before this datetime"),
    channel_title: Optional[str] = Query(None, description="Partial match for channel title"),
    channel_id: Optional[str] = Query(None, description="Exact channel ID"),
    video_id: Optional[str] = Query(None, description="Exact video ID"),
    sort_by: Optional[str] = Query("published_at", description="Sort by field"),
    order: Optional[str] = Query("desc", description="asc or desc"),
    category_id: Optional[List[str]] = Query(None, description="YouTube Category IDs"),
    video_duration: Optional[str] = Query(None, description="Video duration (short|medium|long)"),
    video_type: Optional[str] = Query(None, description="Video type (episode|movie)"),
):
    query = videos.select()
    filters = []

    if title:
        filters.append(videos.c.title.ilike(f"%{title}%"))
    if description:
        filters.append(videos.c.description.ilike(f"%{description}%"))
    if published_after:
        filters.append(videos.c.published_at >= published_after)
    if published_before:
        filters.append(videos.c.published_at <= published_before)
    if channel_title:
        filters.append(videos.c.channel_title.ilike(f"%{channel_title}%"))
    if channel_id:
        filters.append(videos.c.channel_id == channel_id)
    if video_id:
        filters.append(videos.c.video_id == video_id)
    if category_id:
        filters.append(videos.c.category_id.in_(category_id))
    if video_duration:
        filters.append(videos.c.video_duration == video_duration)
    if video_type:
        filters.append(videos.c.video_type == video_type)

    if filters:
        query = query.where(and_(*filters))

    sort_column = getattr(videos.c, sort_by, videos.c.published_at)
    if order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    query = query.limit(limit).offset(offset)
    results = await database.fetch_all(query)
    return results

@app.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    limit: int = Query(12, ge=1, le=50),
    offset: int = Query(0, ge=0),
    title: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    published_after: Optional[str] = Query(None),
    published_before: Optional[str] = Query(None),
    channel_title: Optional[str] = Query(None),
    channel_id: Optional[str] = Query(None),
    video_id: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("published_at"),
    order: Optional[str] = Query("desc"),
):
    params = {
        "limit": limit,
        "offset": offset,
        "title": title,
        "description": description,
        "published_after": published_after,
        "published_before": published_before,
        "channel_title": channel_title,
        "channel_id": channel_id,
        "video_id": video_id,
        "sort_by": sort_by,
        "order": order,
    }
    # Remove None values
    params = {k: v for k, v in params.items() if v not in [None, ""]}
    async with httpx.AsyncClient() as client:
        resp = await client.get("http://localhost:8000/videos", params=params)
        videos_data = resp.json()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "videos": videos_data,
        "categories": YOUTUBE_CATEGORIES,
        "filters": {
            "title": title or "",
            "description": description or "",
            "published_after": published_after or "",
            "published_before": published_before or "",
            "channel_title": channel_title or "",
            "channel_id": channel_id or "",
            "video_id": video_id or "",
            "limit": limit,
            "offset": offset,
            "sort_by": sort_by or "published_at",
            "order": order or "desc",
            "category_ids": request.query_params.getlist("category_id"),
            "video_duration": request.query_params.get("video_duration", ""),
            "video_type": request.query_params.get("video_type", ""),
        }
    })

YOUTUBE_CATEGORIES = [
    {"id": "1", "name": "Film & Animation"},
    {"id": "2", "name": "Autos & Vehicles"},
    {"id": "10", "name": "Music"},
    {"id": "15", "name": "Pets & Animals"},
    {"id": "17", "name": "Sports"},
    {"id": "18", "name": "Short Movies"},
    {"id": "19", "name": "Travel & Events"},
    {"id": "20", "name": "Gaming"},
    {"id": "22", "name": "People & Blogs"},
    {"id": "23", "name": "Comedy"},
    {"id": "24", "name": "Entertainment"},
    {"id": "25", "name": "News & Politics"},
    {"id": "26", "name": "Howto & Style"},
    {"id": "27", "name": "Education"},
    {"id": "28", "name": "Science & Technology"},
    {"id": "29", "name": "Nonprofits & Activism"},
]

@app.get("/categories")
async def get_categories():
    return YOUTUBE_CATEGORIES