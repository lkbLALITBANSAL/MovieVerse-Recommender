
from pathlib import Path
import pickle
from typing import Any

import numpy as np
import pandas as pd


# DATA PATHS

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

MOVIES_FILE = DATA_DIR / "movies_API.pkl"
SIMILARITY_FILE = DATA_DIR / "similarity_API.pkl"
POSTERS_FILE = DATA_DIR / "posters_API.pkl"


# LOAD PICKLE FILES

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


# CLEAN TEXT

def clean_text(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, float) and np.isnan(value):
        return ""

    if isinstance(value, (list, tuple, set, np.ndarray)):
        return ", ".join(clean_text(x) for x in value)

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

    if isinstance(value, (list, tuple, set, np.ndarray)):
        return ", ".join(str(x).strip() for x in value)

    return str(value)


def clean_language(value) -> str:
    if value is None:
        return ""

    code = str(value).strip().lower()

    language_map = {
        "en": "English",
        "hi": "Hindi",
        "es": "Spanish",
        "ja": "Japanese",
        "ko": "Korean",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "zh": "Chinese",
        "ru": "Russian",
        "ar": "Arabic",
        "tr": "Turkish",
        "te": "Telugu",
        "ta": "Tamil",
        "ml": "Malayalam",
        "bn": "Bengali",
        "mr": "Marathi",
        "pa": "Punjabi",
        "th": "Thai",
        "id": "Indonesian",
        "nl": "Dutch",
        "pl": "Polish",
        "sv": "Swedish",
        "da": "Danish",
        "no": "Norwegian",
        "fi": "Finnish",
        "cs": "Czech",
        "hu": "Hungarian",
        "uk": "Ukrainian",
        "fa": "Persian",
        "he": "Hebrew",
        "vi": "Vietnamese",
        "ro": "Romanian",
        "el": "Greek",
    }

    return language_map.get(code, code.upper())


# POSTER LOOKUP

def poster_for(movie_id, title):
    if not posters:
        return None

    candidates = [movie_id, str(movie_id), title]

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
                    posters[id_col].astype(str) == str(movie_id)
                ]

                if not rows.empty:
                    for col in ["poster_url", "poster", "url"]:
                        if (
                            col in posters.columns
                            and pd.notna(rows.iloc[0][col])
                        ):
                            return str(rows.iloc[0][col])

        if "title" in posters.columns:
            rows = posters[
                posters["title"].astype(str).str.lower()
                == str(title).lower()
            ]

            if not rows.empty:
                for col in ["poster_url", "poster", "url"]:
                    if (
                        col in posters.columns
                        and pd.notna(rows.iloc[0][col])
                    ):
                        return str(rows.iloc[0][col])

    return None


# CONVERT MOVIE TO DICTIONARY

def movie_to_dict(row):
    if isinstance(row, pd.Series):
        data = row.to_dict()
    elif isinstance(row, dict):
        data = dict(row)
    else:
        data = dict(row)

    movie_id = data.get("id", data.get("movie_id"))
    title = clean_text(data.get("title"))
    release_date = clean_text(data.get("release_date"))

    year = ""

    if release_date:
        try:
            year = str(pd.to_datetime(release_date).year)
        except Exception:
            year = ""

    runtime = data.get("runtime", 0)

    try:
        runtime = int(float(runtime))
    except Exception:
        runtime = 0

    rating = data.get("rating", data.get("vote_average", 0))

    try:
        rating = float(rating)
    except Exception:
        rating = 0.0

    genres = clean_genres(data.get("genres"))
    cast = clean_text(data.get("cast"))
    keywords = clean_text(data.get("keywords"))

    return {
        "id": movie_id,
        "title": title,
        "overview": clean_text(data.get("overview")),
        "genres": genres,
        "keywords": keywords,
        "release_date": release_date,
        "year": year,
        "cast": cast,
        "director": clean_text(data.get("director")),
        "language": clean_language(data.get("language")),
        "rating": rating,
        "runtime": runtime,
        "poster_url": poster_for(movie_id, title),
    }


# FIND MOVIE INDEX

def find_index(movie_id):
    if isinstance(movies, pd.DataFrame):
        ids = movies["id"].astype(str)
        matches = movies.index[ids == str(movie_id)]

        if len(matches):
            return matches[0]

    for index, row in enumerate(movies):
        data = movie_to_dict(row)

        if str(data["id"]) == str(movie_id):
            return index

    return None


# CONVERT ALL MOVIES TO A LIST

def rows_as_list():
    if isinstance(movies, pd.DataFrame):
        return [
            movie_to_dict(row)
            for _, row in movies.iterrows()
        ]

    return [movie_to_dict(row) for row in movies]
