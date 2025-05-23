from sqlalchemy import Table, Column, String, DateTime, Text
from .db import metadata

videos = Table(
    "videos",
    metadata,
    Column("video_id", String(32), primary_key=True),
    Column("title", String(255),nullable=False),
    Column("description", Text),
    Column("thumbnail_url", String(255)),
    Column("published_at", DateTime(timezone=True),nullable=False, index=True),
    Column("etag", String(64), nullable=False, unique=True),
    Column("channel_id", String(50)),
    Column("channel_title", String(255)),
)