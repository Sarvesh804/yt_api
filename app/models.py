import sqlalchemy as sa
from .db import metadata

videos = sa.Table(
    "videos",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("video_id", sa.String, unique=True, index=True),
    sa.Column("title", sa.String),
    sa.Column("description", sa.Text),
    sa.Column("published_at", sa.DateTime(timezone=True)),
    sa.Column("thumbnail_url", sa.String),
    sa.Column("etag", sa.String),
    sa.Column("channel_id", sa.String),
    sa.Column("channel_title", sa.String),
    sa.Column("category_id", sa.String, nullable=True),
    sa.Column("video_duration", sa.String, nullable=True),
    sa.Column("video_type", sa.String, nullable=True),
)