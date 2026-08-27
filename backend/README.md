# MovieVerse FastAPI Backend

Put these existing files from your current MovieVerse project into `backend/data/`:

- movies_API.pkl
- similarity_API.pkl
- posters_API.pkl

The API provides:

- GET `/health`
- GET `/search?q=dhu`
- GET `/movies/{movie_id}`
- GET `/recommend/{movie_id}?limit=8`
- GET `/top-rated?limit=10`

Run:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend:
http://localhost:8000

Swagger docs:
http://localhost:8000/docs
