from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VideoOut(BaseModel):
    video_id: str
    title: str
    description: Optional[str]
    published_at: datetime
    thumbnail_url: Optional[str]
    etag: str
    channel_id: Optional[str]
    channel_title: Optional[str]

    class Config:
        orm_mode = True