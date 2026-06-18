import streamlit as st
import pandas as pd
import pickle
import numpy as np
from difflib import get_close_matches
from urllib.parse import quote
from streamlit_searchbox import st_searchbox
from rapidfuzz import process
import streamlit.components.v1 as components

def search_movies(searchterm):
    if not searchterm:
        return []

    movie_titles = movies["title"].dropna().tolist()

    results = process.extract(
        searchterm,
        movie_titles,
        limit=10
    )

    return [result[0] for result in results]

st.set_page_config(
    page_title="MovieVerse",
    page_icon="🎬",
    layout="wide",
)

LANGUAGE_MAP = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "ja": "Japanese",
    "ko": "Korean",
    "fr": "French",
    "es": "Spanish",
    "de": "German",
}

MOOD_MAPPING = {
    "😊 Feel Good": ["happy", "comedy", "fun", "family"],
    "😢 Emotional": ["sad", "emotional", "drama", "love"],
    "🚀 Sci-Fi": ["space", "future", "science", "alien"],
    "🔥 Action": ["action", "battle", "war", "fight"],
    "❤️ Romantic": ["romance", "love", "relationship"],
    "😱 Thriller": ["thriller", "crime", "mystery", "suspense"],
    "🤯 Mind Bending": ["mind", "dream", "psychological"],
    "⚔ Adventure": ["adventure", "journey", "fantasy"],
}


@st.cache_data
def load_movies():
    with open("movies_API.pkl", "rb") as f:
        data = pickle.load(f)

    if isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        df = pd.DataFrame(data)

    if "language" in df.columns:
        df["language_display"] = (
            df["language"]
            .fillna("Unknown")
            .astype(str)
            .str.lower()
            .map(LANGUAGE_MAP)
            .fillna(df["language"])
        )

    if "year" not in df.columns:
        if "release_date" in df.columns:
            df["year"] = pd.to_datetime(
                df["release_date"], errors="coerce"
            ).dt.year

    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["tags"] = df["tags"].fillna("").astype(str)

    return df


@st.cache_data
def load_similarity():
    with open("similarity_API.pkl", "rb") as f:
        return pickle.load(f)


@st.cache_data
def load_posters():
    with open("posters_API.pkl", "rb") as f:
        return pickle.load(f)


movies = load_movies()
similarity = load_similarity()
posters = load_posters()

if "selected_mood" not in st.session_state:
    st.session_state.selected_mood = None

st.markdown(
    """
<style>
.main{
    background:#f8fafc;
}

.block-container{
    padding-top:1rem;
    padding-bottom:2rem;
    max-width:1400px;
}

.hero{
    background:linear-gradient(135deg,#2563eb,#7c3aed);
    padding:40px;
    border-radius:24px;
    color:white;
    margin-bottom:30px;
}

.hero-title{
    font-size:3rem;
    font-weight:800;
    margin-bottom:8px;
}

.hero-subtitle{
    font-size:1.1rem;
    opacity:0.95;
}

.movie-card{
    background:white;
    border-radius:18px;
    overflow:hidden;
    box-shadow:0 4px 18px rgba(0,0,0,0.08);
    transition:all .25s ease;
    height:100%;
}

.movie-card:hover{
    transform:translateY(-6px);
    box-shadow:0 10px 28px rgba(0,0,0,0.15);
}

.poster-img{
    width:100%;
    height:340px;
    object-fit:cover;
}

.poster-placeholder{
    height:340px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#e5e7eb;
    color:#6b7280;
    font-size:1rem;
}

.card-body{
    padding:14px;
}

.movie-title{
    font-size:1rem;
    font-weight:700;
    min-height:48px;
    margin-bottom:10px;
}

.movie-meta{
    font-size:0.9rem;
    color:#4b5563;
    margin-bottom:4px;
}

.section-title{
    font-size:1.7rem;
    font-weight:700;
    margin:20px 0;
}

.mood-btn{
    width:100%;
}

.stButton>button{
    border-radius:12px;
}

.tmdb-link{
    text-decoration:none;
}

.search-label{
    font-weight:600;
    margin-bottom:8px;
}
</style>
""",
    unsafe_allow_html=True,
)


def get_poster(movie_id):
    try:
        if isinstance(posters, dict):
            return posters.get(movie_id)
        return None
    except Exception:
        return None


def fuzzy_search(query, titles, limit=15):
    if not query:
        return []

    query_lower = query.lower()

    contains = [
        title
        for title in titles
        if query_lower in str(title).lower()
    ]

    fuzzy = get_close_matches(
        query,
        titles.tolist(),
        n=limit,
        cutoff=0.35,
    )

    merged = []

    for item in contains + fuzzy:
        if item not in merged:
            merged.append(item)

    return merged[:limit]


def apply_filters(df, languages, min_rating, year_range):
    filtered = df.copy()

    if languages:
        filtered = filtered[
            filtered["language_display"].isin(languages)
        ]

    filtered = filtered[
        filtered["rating"].fillna(0) >= min_rating
    ]

    filtered = filtered[
        filtered["year"].fillna(0).between(
            year_range[0],
            year_range[1],
        )
    ]

    return filtered


def get_recommendations(movie_title):
    idx_list = movies.index[
        movies["title"] == movie_title
    ].tolist()

    if not idx_list:
        return pd.DataFrame()

    idx = idx_list[0]

    distances = list(enumerate(similarity[idx]))
    distances = sorted(
        distances,
        key=lambda x: x[1],
        reverse=True,
    )

    recommendations = []

    for movie_idx, _ in distances:
        if movie_idx == idx:
            continue

        recommendations.append(movies.iloc[movie_idx])

        if len(recommendations) >= 100:
            break

    return pd.DataFrame(recommendations)


def mood_discovery(df, mood):
    keywords = MOOD_MAPPING.get(mood, [])

    if not keywords:
        return pd.DataFrame()

    mask = df["tags"].str.lower().apply(
        lambda x: any(k in x for k in keywords)
    )

    return (
        df[mask]
        .sort_values("rating", ascending=False)
        .head(20)
    )


def render_movie_card(movie):
    movie_id = movie.get("id")
    title = movie.get("title", "Unknown")
    rating = movie.get("rating", "N/A")
    language = movie.get("language_display", "Unknown")
    year = (
        int(movie["year"])
        if pd.notna(movie["year"])
        else "N/A"
    )

    poster = get_poster(movie_id)

    if poster:
        poster_html = (
            f'<img src="{poster}" class="poster-img">'
        )
    else:
        poster_html = (
            '<div class="poster-placeholder">'
            'No Poster Available'
            "</div>"
        )

    st.markdown(
        f"""
        <div class="movie-card">
            {poster_html}
            <div class="card-body">
                <div class="movie-title">{title}</div>
                <div class="movie-meta">⭐ {rating}</div>
                <div class="movie-meta">🌐 {language}</div>
                <div class="movie-meta">📅 {year}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.link_button(
        "TMDB",
        f"https://www.themoviedb.org/movie/{movie_id}",
        use_container_width=True,
    )


def render_grid(df):
    if df.empty:
        st.info("No movies found.")
        return

    cols_per_row = 4

    for start in range(0, len(df), cols_per_row):
        cols = st.columns(cols_per_row)

        chunk = df.iloc[start : start + cols_per_row]

        for col, (_, movie) in zip(cols, chunk.iterrows()):
            with col:
                render_movie_card(movie)


st.markdown(
    """
<div class="hero">
    <div class="hero-title">MovieVerse</div>
    <div class="hero-subtitle">
        Discover Movies You'll Love
    </div>
</div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("🎯 Filters")

    language_options = sorted(
        movies["language_display"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_languages = st.multiselect(
        "Language",
        language_options,
    )

    min_rating = st.slider(
        "Minimum Rating",
        0.0,
        10.0,
        0.0,
        0.1,
    )

    valid_years = (
        movies["year"]
        .dropna()
        .astype(int)
        .tolist()
    )

    if valid_years:
        year_min = min(valid_years)
        year_max = max(valid_years)
    else:
        year_min = 1900
        year_max = 2030

    year_range = st.slider(
        "Year Range",
        year_min,
        year_max,
        (year_min, year_max),
    )

filtered_movies = apply_filters(
    movies,
    selected_languages,
    min_rating,
    year_range,
)

st.markdown(
    '<div class="search-label">Search Movie</div>',
    unsafe_allow_html=True,
)

from streamlit_searchbox import st_searchbox
from rapidfuzz import process


def search_movies(searchterm):
    if not searchterm:
        return []

    movie_titles = movies["title"].tolist()

    matches = process.extract(
        searchterm,
        movie_titles,
        limit=10
    )

    return [match[0] for match in matches]


selected_movie = st_searchbox(
    search_function=search_movies,
    placeholder="🔍 Search movies...",
    label="Movie Search",
    key="movie_search"
)

recommend_clicked = st.button(
    "🎬 Recommend",
    use_container_width=True,
)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="section-title">Mood Discovery</div>',
    unsafe_allow_html=True,
)

mood_cols = st.columns(4)

for idx, mood in enumerate(MOOD_MAPPING.keys()):
    with mood_cols[idx % 4]:
        if st.button(
            mood,
            use_container_width=True,
            key=f"mood_{mood}",
        ):
            st.session_state.selected_mood = mood

selected_mood = st.session_state.selected_mood

if selected_mood:
    mood_results = mood_discovery(
        filtered_movies,
        selected_mood,
    )

    st.markdown(
        f"### {selected_mood}"
    )

    if mood_results.empty:
        st.info(
            "No movies available for selected mood."
        )
    else:
        render_grid(mood_results)

if recommend_clicked:
    if not selected_movie:
        st.warning(
            "Please select a movie first."
        )
    else:
        recommendations = get_recommendations(
            selected_movie
        )
        components.html(
        """
        <script>
        setTimeout(function() {
            const target = window.parent.document.getElementById("recommendation-section");
            if (target) {
                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
        }, 500);
        </script>
        """,
        height=0,
        )

        recommendations = apply_filters(
            recommendations,
            selected_languages,
            min_rating,
            year_range,
        )

        recommendations = recommendations.head(20)

        st.markdown(
            
            """
            <div id="recommendation-section"></div>

            <div class="section-title">
            Recommended For You
            </div>
            """,
            unsafe_allow_html=True,
        )

        if recommendations.empty:
            st.info(
                "No recommendations found with current filters."
            )
        else:
            render_grid(recommendations)

st.markdown(
    """
<div class="section-title">
Top Rated Movies
</div>
""",
    unsafe_allow_html=True,
)

top_rated = (
    filtered_movies.sort_values(
        "rating",
        ascending=False,
    )
    .head(12)
)

if top_rated.empty:
    st.info(
        "No top rated movies found."
    )
else:
    render_grid(top_rated)