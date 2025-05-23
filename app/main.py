from fastapi import FastAPI
from contextlib import asynccontextmanager
from .db import database, metadata, engine
from .models import videos

# Create all tables
metadata.create_all(bind=engine)

# Define lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

# Create app with lifespan
app = FastAPI(
    title="Youtube Video Fetcher API",
    version="0.1.0",
    lifespan=lifespan
)

# Health check route
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "API is running!"}
