# YouTube Video Fetcher API

## Features

- Fetches latest YouTube videos for a search query in the background.
- Stores video data in PostgreSQL.
- Provides a paginated API to retrieve videos sorted by publish date.
- Supports multiple API keys for quota management.

## Requirements

- Python 3.10+
- PostgreSQL

## Setup

1. Clone the repo and install dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Set up your `.env` file:

   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/yourdb
   ```

3. Run the server:
   ```
   uvicorn app.main:app --reload
   ```

## API

- **GET /videos?limit=10&offset=0**  
  Returns paginated videos sorted by published date (newest first).

- **GET /health**  
  Health check endpoint.

## Notes

- The background fetcher runs every 10 seconds.
- Add your YouTube API keys in `app/tasks.py` (`API_KEYS` list).
