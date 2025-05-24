# YouTube Video Fetcher API & Dashboard

## Features

- Fetches latest YouTube videos for a search query in the background.
- Stores video data in PostgreSQL.
- Provides a paginated, filterable API to retrieve videos.
- Modern dashboard UI with sidebar filters, search, and pagination (Tailwind CSS).
- Supports multiple API keys for quota management.
- Deep filtering: by title, description, channel, date, category, duration, type, and more.

## Requirements

- Python 3.10+
- PostgreSQL

## Dashboard
![Screenshot 2025-05-24 162507](https://github.com/user-attachments/assets/859c6705-a236-4aa8-9551-60662ffa61df)

![Screenshot 2025-05-24 162520](https://github.com/user-attachments/assets/5ebb8efe-5e94-483e-ab86-5a925ea720ea)


## Setup

1. Clone the repo and install dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Set up your `.env` file:

   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/yourdb
   YOUTUBE_API_KEYS=key1,key2,key3
   ```

3. Create tables:

   ```
   # If you want to reset the videos table (dev only):
   # psql -U user -d yourdb -c "DROP TABLE IF EXISTS videos;"
   ```

4. Run the server:

   ```
   uvicorn app.main:app --reload
   ```

5. Open the dashboard in your browser:
   ```
   http://localhost:8000/
   ```

## API

- **GET /videos**  
  Returns paginated, filterable, and sortable videos.  
  **Query params:**

  - `limit`, `offset`, `title`, `description`, `published_after`, `published_before`,  
    `channel_title`, `channel_id`, `video_id`, `sort_by`, `order`,  
    `category_id` (multi), `video_duration`, `video_type`

- **GET /health**  
  Health check endpoint.

- **GET /**  
  Modern dashboard UI (Jinja2 + Tailwind).

## Notes

- The background fetcher runs every 120 seconds.
- Add your YouTube API keys in `app/tasks.py` (`API_KEYS` list).
- The dashboard supports deep filtering and pagination.
- For best results, ensure your database schema matches `app/models.py`.

---
