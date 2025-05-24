import asyncio
import httpx
from datetime import datetime, timezone, timedelta
from .db import database
from .models import videos
from sqlalchemy.dialects.postgresql import insert as pg_insert
import os
from dotenv import load_dotenv

load_dotenv()

Youtube_api = os.getenv("YOUTUBE_API")
API_KEYS = [Youtube_api]
API_KEY_INDEX = 0

SEARCH_QUERY = "official"
FETCH_INTERVAL = 10 
BASE_URL = "https://www.googleapis.com/youtube/v3/search"


def get_next_api_key():
    global API_KEY_INDEX
    API_KEY_INDEX = (API_KEY_INDEX + 1) % len(API_KEYS)
    return API_KEYS[API_KEY_INDEX]



async def fetch_latest_videos():
    published_after = datetime.now(timezone.utc) - timedelta(minutes=5)

    params = {
        "part": "snippet",
        "q": SEARCH_QUERY,
        "type": "video",
        "order": "date",
        "maxResults": 10,
        "publishedAfter": published_after.isoformat(),
        "key": API_KEYS[API_KEY_INDEX],
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            for item in data.get("items", []):
                snippet = item["snippet"]
                video_data = {
                    "video_id": item["id"]["videoId"],
                    "title": snippet["title"],
                    "description": snippet.get("description"),
                    "published_at": datetime.fromisoformat(item["snippet"]["publishedAt"].replace("Z", "+00:00")),
                    "thumbnail_url": snippet["thumbnails"]["default"]["url"],
                    "etag": item["etag"],
                    "channel_id": snippet.get("channelId"),
                    "channel_title": snippet.get("channelTitle"),
                }

                
                query = pg_insert(videos).values(**video_data).on_conflict_do_nothing(index_elements=["video_id"])
                await database.execute(query)
                print(f"Inserted/Updated video: {video_data['title']}")

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:  # Quota exceeded
                print("Quota exceeded. Switching API key.")
                params["key"] = get_next_api_key()
            else:
                print(f"HTTP error occurred: {e}")
        except Exception as e:
            print(f"Error fetching videos: {e}")