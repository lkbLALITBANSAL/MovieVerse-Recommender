import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from services.movie_service import (
    movies,
    similarity,
    movie_to_dict,
    find_index,
    rows_as_list,
)

app = FastAPI(title="MovieVerse API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://movie-verse-recommender.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "MovieVerse API is running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok", "movies": len(movies)}


@app.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = 8):
    q = q.strip().lower()
    all_movies = rows_as_list()
    starts = []
    contains = []

    for movie in all_movies:
        title = movie["title"].lower()
        if title.startswith(q):
            starts.append(movie)
        elif q in title:
            contains.append(movie)

    result = starts + contains
    return result[:max(1, min(limit, 20))]


@app.get("/movies/{movie_id}")
def get_movie(movie_id: str):
    index = find_index(movie_id)

    if index is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    if isinstance(movies, pd.DataFrame):
        return movie_to_dict(movies.loc[index])

    return movie_to_dict(movies[index])


@app.get("/recommend/{movie_id}")
def recommend(movie_id: str, limit: int = 8):
    index = find_index(movie_id)

    if index is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    distances = np.asarray(similarity[index]).reshape(-1)
    order = np.argsort(distances)[::-1]
    all_movies = rows_as_list()
    results = []

    for candidate_index in order:
        candidate_index = int(candidate_index)

        if candidate_index == int(index):
            continue

        if candidate_index >= len(all_movies):
            continue

        movie = dict(all_movies[candidate_index])
        movie["similarity_score"] = round(
            float(distances[candidate_index]), 4
        )
        results.append(movie)

        if len(results) >= max(1, min(limit, 30)):
            break

    return results


@app.get("/top-rated")
def top_rated(limit: int = 10):
    all_movies = rows_as_list()

    english_movies = [
        movie
        for movie in all_movies
        if movie.get("language", "").strip().lower() == "english"
    ]

    english_movies.sort(
        key=lambda movie: movie.get("rating", 0),
        reverse=True,
    )

    return english_movies[:max(1, min(limit, 10))]


@app.get("/discover")
def discover(
    mood: str = "",
    genre: str = "",
    rating: float = 0,
    language: str = "",
    year_from: int = 0,
    year_to: int = 0,
    exclude: str = "",
):
    all_movies = rows_as_list()
    excluded_ids = set()

    if exclude:
        excluded_ids = {
            x.strip()
            for x in exclude.split(",")
            if x.strip()
        }

    mood_map = {
        "Happy": ["Comedy", "Adventure", "Family", "Animation"],
        "Sad": ["Drama", "Romance"],
        "Romantic": ["Romance", "Drama"],
        "Excited": ["Action", "Adventure", "Thriller"],
        "Chill": ["Comedy", "Drama", "Romance"],
        "Thrilled": ["Thriller", "Horror", "Mystery"],
        "Thoughtful": ["Drama", "Mystery", "Science Fiction"],
        "Funny": ["Comedy", "Family"],
    }

    mood_genres = mood_map.get(mood, [])
    candidates = []

    for movie in all_movies:
        movie_id = str(movie.get("id", ""))

        if movie_id in excluded_ids:
            continue

        movie_genres = str(movie.get("genres", "")).lower()
        movie_rating = float(movie.get("rating", 0) or 0)
        movie_language = str(movie.get("language", "")).lower()

        movie_year = 0
        try:
            movie_year = int(movie.get("year", 0) or 0)
        except Exception:
            movie_year = 0

        if rating and movie_rating < rating:
            continue

        if genre and genre.lower() not in movie_genres:
            continue

        if language and language.lower() not in movie_language:
            continue

        if year_from and movie_year < year_from:
            continue

        if year_to and movie_year > year_to:
            continue

        score = movie_rating

        if mood_genres:
            for mood_genre in mood_genres:
                if mood_genre.lower() in movie_genres:
                    score += 2
                    break

        candidates.append((score, movie))

    candidates.sort(key=lambda x: x[0], reverse=True)
    return [movie for _, movie in candidates]
