
import pickle
import requests
import pandas as pd

from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

API_KEY="7e9ff74b558f6fe0cc08baa01c93cc80"


# -----------------------
# LOAD EXISTING FILES
# -----------------------

movies = pickle.load(
    open("movies_API.pkl", "rb")
)

posters = pickle.load(
    open("posters_API.pkl", "rb")
)

existing_ids = set(
    movies["id"].tolist()
)

print(
    f"Existing Movies: {len(movies)}"
)


# -----------------------
# TMDB HELPERS
# -----------------------

def get_movie_details(movie_id):

    url = (
        f"https://api.themoviedb.org/3/movie/{movie_id}"
        f"?api_key={API_KEY}"
        f"&append_to_response=credits,keywords"
    )

    return requests.get(url).json()


def create_tags(data):

    genres = [
        g["name"]
        for g in data.get(
            "genres",
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

        if crew["job"] == "Director":

            director = crew["name"]
            break

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

    overview = data.get(
        "overview",
        ""
    )

    tags = (
        genres
        + cast
        + [director]
        + keywords
        + [overview]
    )

    return " ".join(
        map(str, tags)
    )


# -----------------------
# FETCH MOVIES
# -----------------------

movie_ids = set()

ENDPOINTS = [
    "popular",
    "top_rated",
    "upcoming",
    "now_playing"
]

for endpoint in ENDPOINTS:

    for page in range(100,120):

        url = (
            f"https://api.themoviedb.org/3/movie/{endpoint}"
            f"?api_key={API_KEY}"
            f"&page={page}"
        )

        try:

            response = requests.get(
                url
            ).json()

            for movie in response.get(
                "results",
                []
            ):

                movie_ids.add(
                    movie["id"]
                )

        except:

            continue


# -----------------------
# NEW MOVIES ONLY
# -----------------------

new_movies = []

for movie_id in movie_ids:

    if movie_id in existing_ids:

        continue

    try:

        data = get_movie_details(
            movie_id
        )

        tags = create_tags(
            data
        )

        release_date = data.get(
            "release_date",
            ""
        )

        year = None

        if release_date:

            year = int(
                release_date[:4]
            )

        poster_path = data.get(
            "poster_path",
            ""
        )

        if (
            poster_path
            and movie_id not in posters
        ):

            posters[movie_id] = (
                "https://image.tmdb.org/t/p/w500"
                + poster_path
            )

        new_movies.append({

            "id":
                movie_id,

            "title":
                data.get(
                    "title",
                    ""
                ),

            "tags":
                tags,

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

            "release_date":
                release_date,

            "year":
                year
        })

    except Exception as e:

        print(
            f"Skipped {movie_id}"
        )

        print(
            "Reason:",
              repr(e)
        )


# -----------------------
# APPEND NEW MOVIES
# -----------------------

print("Fetched IDs:", len(movie_ids))
print("Existing IDs:", len(existing_ids))
print("New IDs:", len(movie_ids - existing_ids))

if len(new_movies) == 0:

    print(
        "No new movies found."
    )

    exit()


new_df = pd.DataFrame(
    new_movies
)

movies = pd.concat(
    [
        movies,
        new_df
    ],
    ignore_index=True
)

print(
    f"Added {len(new_df)} new movies"
)


# -----------------------
# TF-IDF
# -----------------------

ps = PorterStemmer()


def stem(text):

    return " ".join(
        ps.stem(word)
        for word in str(text).split()
    )


movies["tags"] = (
    movies["tags"]
    .fillna("")
    .astype(str)
    .str.lower()
    .apply(stem)
)

tfidf = TfidfVectorizer(
    max_features=10000,
    stop_words="english"
)

vectors = tfidf.fit_transform(
    movies["tags"]
)

similarity = cosine_similarity(
    vectors
)


# -----------------------
# SAVE
# -----------------------

pickle.dump(
    movies,
    open(
        "movies_API.pkl",
        "wb"
    )
)

pickle.dump(
    posters,
    open(
        "posters_API.pkl",
        "wb"
    )
)

pickle.dump(
    similarity,
    open(
        "similarity_API.pkl",
        "wb"
    )
)

print(
    "movies_API.pkl updated"
)

print(
    "posters_API.pkl updated"
)

print(
    "similarity_API.pkl updated"
)

print(
    f"Total Movies: {len(movies)}"
)

