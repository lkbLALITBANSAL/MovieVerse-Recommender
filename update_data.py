import os
import sys
import pickle
import requests
import numpy as np
import pandas as pd

from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


load_dotenv()

TOKEN = os.getenv("TMDB_TOKEN")

if not TOKEN:
    raise ValueError("TMDB_TOKEN is not set in .env")


HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "backend",
    "data"
)


MOVIES_PATH = os.path.join(
    DATA_DIR,
    "movies_API.pkl"
)

EMBEDDINGS_PATH = os.path.join(
    DATA_DIR,
    "embeddings_API.pkl"
)

SIMILARITY_PATH = os.path.join(
    DATA_DIR,
    "similarity_API.pkl"
)

POSTERS_PATH = os.path.join(
    DATA_DIR,
    "posters_API.pkl"
)


LANGUAGES = {
    "hindi": "hi",
    "tamil": "ta",
    "telugu": "te",
    "malayalam": "ml",
    "kannada": "kn",
    "bengali": "bn",
    "marathi": "mr",
    "punjabi": "pa",
    "gujarati": "gu",
    "odia": "or",
    "assamese": "as",

    "english": "en",
    "korean": "ko",
    "japanese": "ja",

    "spanish": "es",
    "french": "fr",
    "german": "de",
    "italian": "it",
    "chinese": "zh",
    "russian": "ru",
    "portuguese": "pt",
    "arabic": "ar",
    "turkish": "tr"
}


def load_pickle(path, default=None):

    if not os.path.exists(path):
        return default

    with open(path, "rb") as file:
        return pickle.load(file)


def save_pickle(path, data):

    with open(path, "wb") as file:
        pickle.dump(data, file)


def get_language():

    if len(sys.argv) < 2:

        print("\nUsage:")
        print(
            "python update_data.py hindi"
        )
        print(
            "python update_data.py tamil"
        )
        print(
            "python update_data.py english"
        )
        print(
            "python update_data.py korean"
        )
        print(
            "python update_data.py japanese"
        )

        print("\nAvailable languages:")

        for language in LANGUAGES:
            print(language)

        sys.exit(1)

    language = sys.argv[1].lower()

    if language not in LANGUAGES:

        print(
            f"\nUnsupported language: {language}"
        )

        print("\nAvailable languages:")

        for language in LANGUAGES:
            print(language)

        sys.exit(1)

    return language, LANGUAGES[language]


def fetch_movies(language_code):

    movies = []

    print(
        f"\nScanning TMDB for "
        f"{language_code} movies..."
    )

    page = 1

    while len(movies) < 100 and page <= 10:

        try:

            response = requests.get(
                "https://api.themoviedb.org/3/discover/movie",
                headers=HEADERS,
                params={
                    "with_original_language":
                        language_code,

                    "sort_by":
                        "popularity.desc",

                    "page":
                        page,

                    "include_adult":
                        "false"
                },
                timeout=15
            )

            if response.status_code != 200:

                print(
                    f"\nTMDB error: "
                    f"{response.status_code}"
                )

                page += 1
                continue

            results = response.json().get(
                "results",
                []
            )

            if not results:
                break

            movies.extend(results)

            print(
                f"\rScanned {len(movies)} movies",
                end=""
            )

            page += 1

        except Exception as e:

            print(
                f"\nError on page {page}: {e}"
            )

            page += 1

    print()

    unique_movies = {}

    for movie in movies:

        unique_movies[
            movie["id"]
        ] = movie

    return list(
        unique_movies.values()
    )[:100]


def get_movie_details(movie_id):

    try:

        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}",
            headers=HEADERS,
            params={
                "append_to_response":
                    "credits,keywords"
            },
            timeout=15
        )

        if response.status_code != 200:
            return None

        return response.json()

    except Exception:
        return None


def fetch_details(movie_ids):

    print(
        f"\nFetching details for "
        f"{len(movie_ids)} movies..."
    )

    movies = []

    completed = 0

    with ThreadPoolExecutor(
        max_workers=10
    ) as executor:

        futures = [
            executor.submit(
                get_movie_details,
                movie_id
            )
            for movie_id in movie_ids
        ]

        for future in as_completed(futures):

            completed += 1

            print(
                f"\rDetails: "
                f"{completed}/{len(movie_ids)}",
                end=""
            )

            result = future.result()

            if result:
                movies.append(result)

    print()

    return movies


def create_dataframe(data):

    rows = []

    for movie in data:

        genres = [
            item["name"]
            for item in movie.get(
                "genres",
                []
            )
        ]

        keywords = [
            item["name"]
            for item in movie.get(
                "keywords",
                {}
            ).get(
                "keywords",
                []
            )
        ]

        cast = [
            item["name"]
            for item in movie.get(
                "credits",
                {}
            ).get(
                "cast",
                []
            )[:5]
        ]

        director = ""

        for crew in movie.get(
            "credits",
            {}
        ).get(
            "crew",
            []
        ):

            if crew.get("job") == "Director":

                director = crew.get(
                    "name",
                    ""
                )

                break

        rows.append({

            "id":
                movie.get("id"),

            "title":
                movie.get(
                    "title",
                    ""
                ),

            "overview":
                movie.get(
                    "overview",
                    ""
                ),

            "genres":
                genres,

            "keywords":
                keywords,

            "cast":
                cast,

            "director":
                director,

            "language":
                movie.get(
                    "original_language",
                    ""
                ),

            "rating":
                movie.get(
                    "vote_average",
                    0
                ),

            "runtime":
                movie.get(
                    "runtime",
                    0
                ),

            "release_date":
                movie.get(
                    "release_date",
                    ""
                ),

            "poster_path":
                movie.get(
                    "poster_path",
                    ""
                )
        })

    return pd.DataFrame(rows)


def create_movie_text(row):

    genres = ", ".join(
        row["genres"]
    )

    keywords = ", ".join(
        row["keywords"]
    )

    cast = ", ".join(
        row["cast"]
    )

    return (
        f"Title: {row['title']} "
        f"Overview: {row['overview']} "
        f"Genres: {genres} "
        f"Keywords: {keywords} "
        f"Cast: {cast} "
        f"Director: {row['director']}"
    )


def prepare_movies(df):

    df["overview"] = (
        df["overview"]
        .fillna("")
        .astype(str)
    )

    df["genres"] = df["genres"].apply(
        lambda x:
        x if isinstance(x, list)
        else []
    )

    df["keywords"] = df["keywords"].apply(
        lambda x:
        x if isinstance(x, list)
        else []
    )

    df["cast"] = df["cast"].apply(
        lambda x:
        x if isinstance(x, list)
        else []
    )

    df["tags"] = df.apply(
        create_movie_text,
        axis=1
    )

    df["year"] = pd.to_datetime(
        df["release_date"],
        errors="coerce"
    ).dt.year

    return df[
        [
            "id",
            "title",
            "overview",
            "genres",
            "keywords",
            "cast",
            "director",
            "language",
            "rating",
            "runtime",
            "release_date",
            "year",
            "poster_path",
            "tags"
        ]
    ].copy()


def has_poster(poster):

    if poster is None:
        return False

    if pd.isna(poster):
        return False

    return str(poster).strip() != ""


def filter_movies_with_posters(
    movies,
    posters
):

    keep_indexes = []

    for index, row in movies.iterrows():

        movie_id = row["id"]

        poster = None

        if isinstance(posters, dict):

            poster = posters.get(
                movie_id
            )

            if poster is None:

                poster = posters.get(
                    str(movie_id)
                )

        if has_poster(poster):

            keep_indexes.append(index)

    return keep_indexes


def create_embeddings(movies):

    print(
        "\nLoading multilingual model..."
    )

    model = SentenceTransformer(
        "paraphrase-multilingual-MiniLM-L12-v2"
    )

    print(
        "Creating embeddings..."
    )

    embeddings = model.encode(
        movies["tags"].tolist(),
        show_progress_bar=True,
        normalize_embeddings=True
    )

    return np.asarray(
        embeddings
    )


def update_posters(
    old_posters,
    movies
):

    if old_posters is None:
        old_posters = {}

    posters = dict(
        old_posters
    )

    for _, movie in movies.iterrows():

        movie_id = movie["id"]

        poster_path = movie[
            "poster_path"
        ]

        if has_poster(
            poster_path
        ):

            posters[movie_id] = (
                "https://image.tmdb.org/t/p/w500"
                + str(poster_path)
            )

    return posters


def main():

    print(
        "\n========================================"
    )

    print(
        "       MOVIEVERSE DATA UPDATER"
    )

    print(
        "========================================"
    )

    language_name, language_code = (
        get_language()
    )

    print(
        f"\nSelected language: "
        f"{language_name}"
    )

    old_movies = load_pickle(
        MOVIES_PATH
    )

    old_embeddings = load_pickle(
        EMBEDDINGS_PATH
    )

    old_posters = load_pickle(
        POSTERS_PATH,
        {}
    )

    if old_movies is None:

        raise FileNotFoundError(
            "movies_API.pkl was not found."
        )

    if not isinstance(
        old_movies,
        pd.DataFrame
    ):

        old_movies = pd.DataFrame(
            old_movies
        )

    old_movies = old_movies.copy()

    print(
        f"\nExisting movies: "
        f"{len(old_movies)}"
    )

    existing_ids = set(
        old_movies["id"]
        .astype(str)
    )

    candidates = fetch_movies(
        language_code
    )

    new_ids = []

    for movie in candidates:

        movie_id = str(
            movie["id"]
        )

        if movie_id not in existing_ids:

            new_ids.append(
                movie["id"]
            )

        if len(new_ids) >= 100:
            break

    print(
        f"New candidates: "
        f"{len(new_ids)}"
    )

    if not new_ids:

        print(
            "\nNo new movies found."
        )

        return

    details = fetch_details(
        new_ids
    )

    if not details:

        print(
            "\nNo movie details found."
        )

        return

    new_movies = create_dataframe(
        details
    )

    new_movies = prepare_movies(
        new_movies
    )

    new_movies = new_movies[
        ~new_movies["id"]
        .astype(str)
        .isin(existing_ids)
    ]

    print(
        f"\nNew movies after duplicate check: "
        f"{len(new_movies)}"
    )

    if len(new_movies) == 0:

        print(
            "\nNo genuinely new movies."
        )

        return

    new_posters = {}

    for _, movie in new_movies.iterrows():

        poster_path = movie[
            "poster_path"
        ]

        if has_poster(
            poster_path
        ):

            new_posters[
                movie["id"]
            ] = (
                "https://image.tmdb.org/t/p/w500"
                + str(poster_path)
            )

    new_movies = new_movies[
        new_movies["id"].isin(
            new_posters.keys()
        )
    ].reset_index(drop=True)

    print(
        f"New movies with posters: "
        f"{len(new_movies)}"
    )

    if len(new_movies) == 0:

        print(
            "\nNone of the new movies "
            "has a poster."
        )

        return

    combined_movies = pd.concat(
        [
            old_movies,
            new_movies
        ],
        ignore_index=True
    )

    combined_posters = dict(
        old_posters
    )

    combined_posters.update(
        new_posters
    )

    print(
        "\nChecking existing movies "
        "for missing posters..."
    )

    keep_indexes = (
        filter_movies_with_posters(
            combined_movies,
            combined_posters
        )
    )

    removed_count = (
        len(combined_movies)
        - len(keep_indexes)
    )

    print(
        f"Movies without posters removed: "
        f"{removed_count}"
    )

    combined_movies = combined_movies.iloc[
        keep_indexes
    ].reset_index(drop=True)

    valid_ids = set(
        combined_movies["id"]
        .astype(str)
    )

    cleaned_posters = {}

    for movie_id, poster in (
        combined_posters.items()
    ):

        if (
            str(movie_id)
            in valid_ids
            and has_poster(poster)
        ):

            cleaned_posters[
                movie_id
            ] = poster

    print(
        f"\nFinal movie count: "
        f"{len(combined_movies)}"
    )

    print(
        "\nCreating embeddings..."
    )

    old_id_to_embedding = {}

    if old_embeddings is not None:

        old_embeddings = np.asarray(
            old_embeddings
        )

        old_ids = old_movies[
            "id"
        ].astype(str).tolist()

        for i, movie_id in enumerate(
            old_ids
        ):

            old_id_to_embedding[
                movie_id
            ] = old_embeddings[i]

    model = SentenceTransformer(
        "paraphrase-multilingual-MiniLM-L12-v2"
    )

    new_embeddings = model.encode(
        new_movies["tags"].tolist(),
        show_progress_bar=True,
        normalize_embeddings=True
    )

    new_embedding_map = {}

    for i, movie_id in enumerate(
        new_movies["id"]
    ):

        new_embedding_map[
            str(movie_id)
        ] = new_embeddings[i]

    final_embeddings = []

    for _, movie in combined_movies.iterrows():

        movie_id = str(
            movie["id"]
        )

        if movie_id in old_id_to_embedding:

            final_embeddings.append(
                old_id_to_embedding[
                    movie_id
                ]
            )

        elif movie_id in new_embedding_map:

            final_embeddings.append(
                new_embedding_map[
                    movie_id
                ]
            )

    final_embeddings = np.asarray(
        final_embeddings
    )

    if len(final_embeddings) != len(
        combined_movies
    ):

        raise ValueError(
            "Movie and embedding counts "
            "do not match."
        )

    print(
        f"\nFinal embeddings: "
        f"{final_embeddings.shape}"
    )

    print(
        "\nCreating COMPLETE similarity matrix..."
    )

    similarity = cosine_similarity(
        final_embeddings
    )

    print(
        f"Similarity matrix: "
        f"{similarity.shape}"
    )

    if similarity.shape[0] != len(
        combined_movies
    ):

        raise ValueError(
            "Similarity matrix size "
            "does not match movies."
        )

    print(
        "\nSaving files..."
    )

    save_pickle(
        MOVIES_PATH,
        combined_movies
    )

    save_pickle(
        EMBEDDINGS_PATH,
        final_embeddings
    )

    save_pickle(
        SIMILARITY_PATH,
        similarity
    )

    save_pickle(
        POSTERS_PATH,
        cleaned_posters
    )

    print(
        "\n========================================"
    )

    print(
        "          UPDATE COMPLETE"
    )

    print(
        "========================================"
    )

    print(
        f"\nExisting movies      : "
        f"{len(old_movies)}"
    )

    print(
        f"New movies added     : "
        f"{len(new_movies)}"
    )

    print(
        f"No-poster removed    : "
        f"{removed_count}"
    )

    print(
        f"Final movies         : "
        f"{len(combined_movies)}"
    )

    print(
        f"Embeddings           : "
        f"{final_embeddings.shape}"
    )

    print(
        f"Similarity            : "
        f"{similarity.shape}"
    )

    print(
        f"Posters               : "
        f"{len(cleaned_posters)}"
    )

    print(
        "\nUpdated files:"
    )

    print(
        "✓ movies_API.pkl"
    )

    print(
        "✓ embeddings_API.pkl"
    )

    print(
        "✓ similarity_API.pkl"
    )

    print(
        "✓ posters_API.pkl"
    )


if __name__ == "__main__":
    main()