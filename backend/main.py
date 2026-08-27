# backend/main.py

from pathlib import Path
import pickle
from typing import Any

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

MOVIES_FILE = DATA_DIR / "movies_API.pkl"
SIMILARITY_FILE = DATA_DIR / "similarity_API.pkl"
POSTERS_FILE = DATA_DIR / "posters_API.pkl"

app = FastAPI(title="MovieVerse API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


def load_pickle(path):
    if not path.exists():
        raise FileNotFoundError(
            f"{path.name} was not found in {DATA_DIR}"
        )

    with open(path, "rb") as file:
        return pickle.load(file)


movies = load_pickle(MOVIES_FILE)
similarity = load_pickle(SIMILARITY_FILE)

try:
    posters = load_pickle(POSTERS_FILE)
except FileNotFoundError:
    posters = {}


def clean_text(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, float) and np.isnan(value):
        return ""

    if isinstance(value, (list, tuple, set, np.ndarray)):
        return ", ".join(
            clean_text(x) for x in value
        )

    return str(value)


def clean_genres(value) -> str:
    if value is None:
        return ""

    if isinstance(value, str):
        value = value.strip()

        if value.startswith("[") and value.endswith("]"):
            value = value[1:-1]

            if not value.strip():
                return ""

            return ", ".join(
                x.strip().strip("'\"")
                for x in value.split(",")
            )

        return value

    if isinstance(
        value,
        (list, tuple, set, np.ndarray)
    ):
        return ", ".join(
            str(x).strip()
            for x in value
        )

    return str(value)


def poster_for(movie_id, title):

    if not posters:
        return None

    candidates = [
        movie_id,
        str(movie_id),
        title
    ]

    if isinstance(posters, dict):

        for key in candidates:

            if key in posters:

                value = posters[key]

                if isinstance(value, dict):
                    return (
                        value.get("poster_url")
                        or value.get("poster")
                        or value.get("url")
                    )

                if value:
                    return str(value)

    if isinstance(posters, pd.DataFrame):

        for id_col in ["id", "movie_id"]:

            if id_col in posters.columns:

                rows = posters[
                    posters[id_col].astype(str)
                    == str(movie_id)
                ]

                if not rows.empty:

                    for col in [
                        "poster_url",
                        "poster",
                        "url"
                    ]:

                        if (
                            col in posters.columns
                            and pd.notna(
                                rows.iloc[0][col]
                            )
                        ):
                            return str(
                                rows.iloc[0][col]
                            )

        if "title" in posters.columns:

            rows = posters[
                posters["title"]
                .astype(str)
                .str.lower()
                == str(title).lower()
            ]

            if not rows.empty:

                for col in [
                    "poster_url",
                    "poster",
                    "url"
                ]:

                    if (
                        col in posters.columns
                        and pd.notna(
                            rows.iloc[0][col]
                        )
                    ):
                        return str(
                            rows.iloc[0][col]
                        )

    return None


def movie_to_dict(row):

    if isinstance(row, pd.Series):
        data = row.to_dict()

    elif isinstance(row, dict):
        data = dict(row)

    else:
        data = dict(row)

    movie_id = data.get(
        "id",
        data.get("movie_id")
    )

    title = clean_text(
        data.get("title")
    )

    release_date = clean_text(
        data.get("release_date")
    )

    year = ""

    if release_date:

        try:
            year = str(
                pd.to_datetime(
                    release_date
                ).year
            )
        except Exception:
            year = ""

    runtime = data.get(
        "runtime",
        0
    )

    try:
        runtime = int(
            float(runtime)
        )
    except Exception:
        runtime = 0

    rating = data.get(
        "rating",
        data.get(
            "vote_average",
            0
        )
    )

    try:
        rating = float(rating)
    except Exception:
        rating = 0.0

    genres = clean_genres(
        data.get("genres")
    )

    cast = clean_text(
        data.get("cast")
    )

    keywords = clean_text(
        data.get("keywords")
    )

    return {
        "id": movie_id,
        "title": title,
        "overview": clean_text(
            data.get("overview")
        ),
        "genres": genres,
        "keywords": keywords,
        "release_date": release_date,
        "year": year,
        "cast": cast,
        "director": clean_text(
            data.get("director")
        ),
        "language": clean_text(
            data.get("language")
        ),
        "rating": rating,
        "runtime": runtime,
        "poster_url": poster_for(
            movie_id,
            title
        )
    }


def find_index(movie_id):

    if isinstance(
        movies,
        pd.DataFrame
    ):

        ids = movies["id"].astype(str)

        matches = movies.index[
            ids == str(movie_id)
        ]

        if len(matches):
            return matches[0]

    for index, row in enumerate(movies):

        data = movie_to_dict(row)

        if str(data["id"]) == str(movie_id):
            return index

    return None


def rows_as_list():

    if isinstance(
        movies,
        pd.DataFrame
    ):

        return [
            movie_to_dict(row)
            for _, row in movies.iterrows()
        ]

    return [
        movie_to_dict(row)
        for row in movies
    ]


@app.get("/")
def root():

    return {
        "message": "MovieVerse API is running",
        "docs": "/docs"
    }


@app.get("/health")
def health():

    return {
        "status": "ok",
        "movies": len(movies)
    }


@app.get("/search")
def search(
    q: str = Query(
        ...,
        min_length=1
    ),
    limit: int = 8
):

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

    return result[
        :max(1, min(limit, 20))
    ]


@app.get("/movies/{movie_id}")
def get_movie(movie_id: str):

    index = find_index(movie_id)

    if index is None:
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    if isinstance(
        movies,
        pd.DataFrame
    ):

        return movie_to_dict(
            movies.loc[index]
        )

    return movie_to_dict(
        movies[index]
    )


@app.get("/recommend/{movie_id}")
def recommend(
    movie_id: str,
    limit: int = 8
):

    index = find_index(movie_id)

    if index is None:
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    distances = np.asarray(
        similarity[index]
    ).reshape(-1)

    order = np.argsort(
        distances
    )[::-1]

    all_movies = rows_as_list()

    results = []

    for candidate_index in order:

        candidate_index = int(
            candidate_index
        )

        if candidate_index == int(index):
            continue

        if candidate_index >= len(all_movies):
            continue

        movie = dict(
            all_movies[candidate_index]
        )

        movie["similarity_score"] = round(
            float(
                distances[candidate_index]
            ),
            4
        )

        results.append(movie)

        if len(results) >= max(
            1,
            min(limit, 30)
        ):
            break

    return results


@app.get("/top-rated")
def top_rated(
    limit: int = 10
):

    all_movies = rows_as_list()

    all_movies.sort(
        key=lambda movie: movie.get(
            "rating",
            0
        ),
        reverse=True
    )

    return all_movies[
        :max(1, min(limit, 30))
    ]