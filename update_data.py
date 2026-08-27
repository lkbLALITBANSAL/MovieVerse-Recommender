import os
import time
import pickle
import requests
import pandas as pd

from dotenv import load_dotenv
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


load_dotenv()

TOKEN = os.getenv("TMDB_TOKEN")

if not TOKEN:
    raise ValueError(
        "TMDB_TOKEN is not set in .env"
    )


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

os.makedirs(
    DATA_DIR,
    exist_ok=True
)


session = requests.Session()


def get_complete_movie(movie_id):

    url = (
        f"https://api.themoviedb.org/3/movie/{movie_id}"
        "?append_to_response=credits,keywords"
    )

    try:

        response = session.get(
            url,
            headers=HEADERS,
            timeout=30
        )

        if response.status_code != 200:
            print(
                f"Movie {movie_id} failed: "
                f"{response.status_code}"
            )
            return None

        return response.json()

    except Exception as e:

        print(
            f"Movie {movie_id} error: {e}"
        )

        return None


def get_movies():

    movies = []

    print("Fetching popular movies...")

    for page in range(1, 50):

        try:

            response = session.get(
                "https://api.themoviedb.org/3/movie/popular",
                headers=HEADERS,
                params={"page": page},
                timeout=30
            )

            if response.status_code != 200:

                print(
                    f"Page {page} failed: "
                    f"{response.status_code}"
                )

                continue

            results = response.json().get(
                "results",
                []
            )

            movies.extend(results)

            print(
                f"Page {page}/49 completed"
            )

            time.sleep(1)

        except Exception as e:

            print(
                f"Page {page} error: {e}"
            )

    print(
        "Total movies fetched:",
        len(movies)
    )

    return movies


def create_dataframe(movies):

    movies_data = []

    print(
        "Fetching complete movie details..."
    )

    for movie in tqdm(
        movies[:600]
    ):

        data = get_complete_movie(
            movie["id"]
        )

        if not data:
            continue

        genres = [
            g["name"]
            for g in data.get(
                "genres",
                []
            )
        ]

        keywords = [
            k["name"]
            for k in data.get(
                "keywords",
                {}
            ).get(
                "keywords",
                []
            )
        ]

        cast = [
            actor["name"]
            for actor in data.get(
                "credits",
                {}
            ).get(
                "cast",
                []
            )[:5]
        ]

        director = ""

        for crew in data.get(
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

        movies_data.append({

            "id":
                data.get(
                    "id"
                ),

            "title":
                data.get(
                    "title",
                    ""
                ),

            "overview":
                data.get(
                    "overview",
                    ""
                ),

            "genres":
                genres,

            "keywords":
                keywords,

            "release_date":
                data.get(
                    "release_date",
                    ""
                ),

            "cast":
                cast,

            "director":
                director,

            "language":
                data.get(
                    "original_language",
                    ""
                ),

            "rating":
                data.get(
                    "vote_average",
                    0
                ),

            "runtime":
                data.get(
                    "runtime",
                    0
                ),

            "poster_path":
                data.get(
                    "poster_path",
                    ""
                )
        })

        time.sleep(0.1)

    df = pd.DataFrame(
        movies_data
    )

    return df


def prepare_data(df):

    df["overview"] = (
        df["overview"]
        .fillna("")
        .astype(str)
    )

    df["director"] = (
        df["director"]
        .fillna("")
        .astype(str)
    )

    df["genres"] = df["genres"].apply(
        lambda x:
            x if isinstance(
                x,
                list
            )
            else []
    )

    df["keywords"] = df["keywords"].apply(
        lambda x:
            x if isinstance(
                x,
                list
            )
            else []
    )

    df["cast"] = df["cast"].apply(
        lambda x:
            x if isinstance(
                x,
                list
            )
            else []
    )

    return df


def make_movie_text(row):

    genres = ", ".join(
        row["genres"]
    )

    keywords = ", ".join(
        row["keywords"]
    )

    cast = ", ".join(
        row["cast"]
    )

    director = row["director"]

    return (
        f"Overview: {row['overview']} "
        f"Genres: {genres} "
        f"Keywords: {keywords} "
        f"Cast: {cast} "
        f"Director: {director}"
    )


def create_movies_dataframe(df):

    df["tags"] = df.apply(
        make_movie_text,
        axis=1
    )

    movies = df[[
        "id",
        "title",
        "overview",
        "genres",
        "tags",
        "language",
        "rating",
        "runtime",
        "release_date",
        "poster_path"
    ]].copy()

    movies["year"] = pd.to_datetime(
        movies["release_date"],
        errors="coerce"
    ).dt.year

    return movies


def create_embeddings(movies):

    print(
        "\nLoading SBERT model..."
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

    print(
        "Embedding Shape:",
        embeddings.shape
    )

    return embeddings


def create_similarity(embeddings):

    print(
        "Creating similarity matrix..."
    )

    similarity = cosine_similarity(
        embeddings
    )

    print(
        "Similarity Shape:",
        similarity.shape
    )

    return similarity


def create_posters(movies):

    print(
        "\nCreating poster dictionary..."
    )

    poster_dict = {}

    for _, movie in tqdm(
        movies.iterrows(),
        total=len(movies)
    ):

        movie_id = movie["id"]

        poster_path = movie[
            "poster_path"
        ]

        if pd.notna(
            poster_path
        ) and poster_path:

            poster_dict[
                movie_id
            ] = (
                "https://image.tmdb.org/t/p/w500"
                + str(poster_path)
            )

        else:

            poster_dict[
                movie_id
            ] = ""

    return poster_dict


def save_data(
    movies,
    embeddings,
    similarity,
    poster_dict
):

    print(
        "\nSaving files..."
    )

    movies_path = os.path.join(
        DATA_DIR,
        "movies_API.pkl"
    )

    embeddings_path = os.path.join(
        DATA_DIR,
        "embeddings_API.pkl"
    )

    similarity_path = os.path.join(
        DATA_DIR,
        "similarity_API.pkl"
    )

    posters_path = os.path.join(
        DATA_DIR,
        "posters_API.pkl"
    )

    with open(
        movies_path,
        "wb"
    ) as file:

        pickle.dump(
            movies,
            file
        )

    with open(
        embeddings_path,
        "wb"
    ) as file:

        pickle.dump(
            embeddings,
            file
        )

    with open(
        similarity_path,
        "wb"
    ) as file:

        pickle.dump(
            similarity,
            file
        )

    with open(
        posters_path,
        "wb"
    ) as file:

        pickle.dump(
            poster_dict,
            file
        )

    print(
        "\nAll files updated successfully."
    )

    print(
        "Movies:",
        movies_path
    )

    print(
        "Embeddings:",
        embeddings_path
    )

    print(
        "Similarity:",
        similarity_path
    )

    print(
        "Posters:",
        posters_path
    )


def main():

    print(
        "================================"
    )

    print(
        "       MOVIEVERSE DATA UPDATE"
    )

    print(
        "================================\n"
    )

    movies = get_movies()

    if not movies:

        raise RuntimeError(
            "No movies were fetched."
        )

    df = create_dataframe(
        movies
    )

    print(
        "\nDataFrame created:"
    )

    print(
        df.shape
    )

    df = prepare_data(
        df
    )

    movies_df = create_movies_dataframe(
        df
    )

    print(
        "\nMovie dataframe:"
    )

    print(
        movies_df[
            [
                "id",
                "title",
                "overview",
                "genres",
                "rating"
            ]
        ].head()
    )

    embeddings = create_embeddings(
        movies_df
    )

    similarity = create_similarity(
        embeddings
    )

    poster_dict = create_posters(
        movies_df
    )

    save_data(
        movies_df,
        embeddings,
        similarity,
        poster_dict
    )

    print(
        "\n================================"
    )

    print(
        "       UPDATE COMPLETE"
    )

    print(
        "================================"
    )


if __name__ == "__main__":
    main()