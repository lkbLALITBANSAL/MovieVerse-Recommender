import { useEffect, useState } from "react";
import {
  searchMovies,
  getMovie,
  getRecommendations,
  getTopRated,
  discoverMovies
} from "./api";

function App() {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [topRated, setTopRated] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [mood, setMood] = useState("");
  const [genre, setGenre] = useState("");
  const [rating, setRating] = useState("");
  const [language, setLanguage] = useState("");
  const [yearFrom, setYearFrom] = useState("");
  const [yearTo, setYearTo] = useState("");

  const [discoverMovie, setDiscoverMovie] = useState(null);
  const [excludedMovies, setExcludedMovies] = useState([]);
  const [discoverLoading, setDiscoverLoading] = useState(false);
  const [discoverError, setDiscoverError] = useState("");

  useEffect(() => {
    loadTopRated();
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (query.trim().length >= 1) {
        loadSuggestions(query);
      } else {
        setSuggestions([]);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [query]);

  async function loadSuggestions(value) {
    try {
      const data = await searchMovies(value);
      setSuggestions(data || []);
    } catch {
      setSuggestions([]);
    }
  }

  async function loadTopRated() {
    try {
      const data = await getTopRated(10);
      setTopRated(data || []);
    } catch {
      setTopRated([]);
    }
  }

  async function selectMovie(movie) {
    setSuggestions([]);
    setQuery(movie.title);
    setLoading(true);
    setError("");

    try {
      const details = await getMovie(movie.id);
      const related = await getRecommendations(movie.id, 8);

      setSelectedMovie(details);
      setRecommendations(related || []);

      setTimeout(() => {
        document
          .getElementById("movie-details")
          ?.scrollIntoView({
            behavior: "smooth",
            block: "start"
          });
      }, 100);
    } catch {
      setError("Unable to load movie details.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSearch(e) {
    e.preventDefault();

    if (!query.trim()) return;

    setError("");

    try {
      const data = await searchMovies(query);

      if (data && data.length > 0) {
        selectMovie(data[0]);
      } else {
        setError("Movie not found.");
      }
    } catch {
      setError("Unable to connect to MovieVerse backend.");
    }
  }

  async function findMovie(regenerate = false) {
    setDiscoverLoading(true);
    setDiscoverError("");

    try {
      const result = await discoverMovies({
        mood,
        genre,
        rating,
        language,
        yearFrom,
        yearTo,
        exclude: regenerate ? excludedMovies : []
      });

      if (!result || result.length === 0) {
        setDiscoverMovie(null);
        setDiscoverError(
          "No movie matches these preferences. Try changing the filters."
        );
        return;
      }

      let available = result.filter(
        movie =>
          !excludedMovies.includes(String(movie.id))
      );

      if (available.length === 0) {
        setExcludedMovies([]);
        available = result;
      }

      const randomIndex = Math.floor(
        Math.random() * available.length
      );

      const movie = available[randomIndex];

      setDiscoverMovie(movie);

      setExcludedMovies(prev => {
        const id = String(movie.id);

        if (prev.includes(id)) {
          return prev;
        }

        return [...prev, id];
      });

      setTimeout(() => {
        document
          .getElementById("discover-result")
          ?.scrollIntoView({
            behavior: "smooth",
            block: "center"
          });
      }, 100);
    } catch (err) {
      console.error(err);
      setDiscoverError(
        "Unable to find a movie. Please try again."
      );
    } finally {
      setDiscoverLoading(false);
    }
  }

  function clearFilters() {
    setMood("");
    setGenre("");
    setRating("");
    setLanguage("");
    setYearFrom("");
    setYearTo("");
    setDiscoverMovie(null);
    setExcludedMovies([]);
    setDiscoverError("");
  }

  function scrollToFinder() {
    document
      .getElementById("movie-finder")
      ?.scrollIntoView({
        behavior: "smooth"
      });
  }

  function MovieCard({ movie }) {
    return (
      <div
        className="movie-card"
        onClick={() => selectMovie(movie)}
      >
        {movie.poster_url ? (
          <img
            src={movie.poster_url}
            alt={movie.title}
          />
        ) : (
          <div className="no-poster">
            🎬
          </div>
        )}

        <div className="movie-card-info">

          <h3>{movie.title}</h3>

          <div className="card-meta">

            <span>
              ⭐{" "}
              {movie.rating
                ? Number(movie.rating).toFixed(1)
                : "N/A"}
            </span>

            {movie.year && (
              <span>{movie.year}</span>
            )}

          </div>

          {movie.genres && (
            <p>{movie.genres}</p>
          )}

        </div>
      </div>
    );
  }

  return (
    <div className="app">

      <header className="navbar">

        <div
          className="logo"
          onClick={() => {
            window.scrollTo({
              top: 0,
              behavior: "smooth"
            });
          }}
        >
          <span>🎬</span>
          <span>MovieVerse</span>
        </div>

        <nav>

          <button
            onClick={() =>
              window.scrollTo({
                top: 0,
                behavior: "smooth"
              })
            }
          >
            Home
          </button>

          <button onClick={scrollToFinder}>
            Find by Mood
          </button>

          <button
            onClick={() =>
              document
                .getElementById("top-rated")
                ?.scrollIntoView({
                  behavior: "smooth"
                })
            }
          >
            Top Rated
          </button>

        </nav>

      </header>


      <main>

        <section className="hero">

          <div className="hero-content">

            <p className="hero-small">
              WELCOME TO MOVIEVERSE
            </p>

            <h1>
              Discover your next
              <span> favorite movie.</span>
            </h1>

            <p className="hero-description">
              Search movies or let MovieVerse
              find the perfect movie based on
              your mood and preferences.
            </p>

            <form
              className="search-box"
              onSubmit={handleSearch}
            >

              <span>🔍</span>

              <input
                type="text"
                value={query}
                placeholder="Search for a movie..."
                onChange={e =>
                  setQuery(e.target.value)
                }
              />

              <button type="submit">
                Search
              </button>


              {suggestions.length > 0 && (

                <div className="suggestions">

                  {suggestions
                    .slice(0, 6)
                    .map(movie => (

                      <div
                        className="suggestion"
                        key={movie.id}
                        onClick={() =>
                          selectMovie(movie)
                        }
                      >

                        {movie.poster_url ? (

                          <img
                            src={movie.poster_url}
                            alt=""
                          />

                        ) : (

                          <div className="suggestion-poster">
                            🎬
                          </div>

                        )}

                        <div>

                          <strong>
                            {movie.title}
                          </strong>

                          <small>
                            {movie.year || ""}

                            {movie.rating
                              ? ` • ⭐ ${Number(
                                  movie.rating
                                ).toFixed(1)}`
                              : ""}
                          </small>

                        </div>

                      </div>

                    ))}

                </div>

              )}

            </form>


            <button
              className="mood-hero-button"
              onClick={scrollToFinder}
            >
              ✨ Find a Movie for My Mood
            </button>

          </div>

        </section>


        {error && (
          <div className="error-message">
            {error}
          </div>
        )}


        {loading && (
          <div className="loading">
            Loading movie...
          </div>
        )}


        {selectedMovie && (

          <section
            className="movie-details-section"
            id="movie-details"
          >

            <div className="section-heading">

              <p>YOUR MOVIE</p>

              <h2>Movie Details</h2>

            </div>


            <div className="movie-details">

              <div className="main-poster">

                {selectedMovie.poster_url ? (

                  <img
                    src={selectedMovie.poster_url}
                    alt={selectedMovie.title}
                  />

                ) : (

                  <div className="large-no-poster">
                    🎬
                  </div>

                )}

              </div>


              <div className="movie-info">

                <h1>
                  {selectedMovie.title}
                </h1>


                <div className="movie-tags">

                  {selectedMovie.rating > 0 && (

                    <span className="rating">
                      ⭐{" "}
                      {Number(
                        selectedMovie.rating
                      ).toFixed(1)}
                    </span>

                  )}

                  {selectedMovie.year && (
                    <span>
                      📅 {selectedMovie.year}
                    </span>
                  )}

                  {selectedMovie.runtime > 0 && (
                    <span>
                      ⏱ {selectedMovie.runtime} min
                    </span>
                  )}

                </div>


                {selectedMovie.genres && (

                  <div className="detail-row">

                    <strong>
                      Genres
                    </strong>

                    <span>
                      {selectedMovie.genres}
                    </span>

                  </div>

                )}


                {selectedMovie.language && (

                  <div className="detail-row">

                    <strong>
                      Language
                    </strong>

                    <span>
                      {selectedMovie.language}
                    </span>

                  </div>

                )}


                {selectedMovie.director && (

                  <div className="detail-row">

                    <strong>
                      Director
                    </strong>

                    <span>
                      {selectedMovie.director}
                    </span>

                  </div>

                )}


                {selectedMovie.cast && (

                  <div className="detail-row">

                    <strong>
                      Cast
                    </strong>

                    <span>
                      {selectedMovie.cast}
                    </span>

                  </div>

                )}


                {selectedMovie.overview && (

                  <div className="overview">

                    <h3>
                      Overview
                    </h3>

                    <p>
                      {selectedMovie.overview}
                    </p>

                  </div>

                )}

              </div>

            </div>

          </section>

        )}


        {selectedMovie &&
          recommendations.length > 0 && (

            <section className="content-section">

              <div className="section-heading">

                <p>
                  BECAUSE YOU LIKED IT
                </p>

                <h2>
                  Related Movies
                </h2>

              </div>


              <div className="movie-grid">

                {recommendations.map(movie => (

                  <MovieCard
                    key={movie.id}
                    movie={movie}
                  />

                ))}

              </div>

            </section>

          )}


        <section
          className="finder-section"
          id="movie-finder"
        >

          <div className="finder-header">

            <div>

              <p className="section-label">
                MOVIE DISCOVERY
              </p>

              <h2>
                🎭 Find a Movie
                <span>
                  {" "}for Your Mood
                </span>
              </h2>

              <p>
                Tell us what you're in the mood
                for and we'll pick one movie
                from our collection.
              </p>

            </div>

          </div>


          <div className="finder-box">

            <div className="filter-group">

              <label>
                How is your mood today?
              </label>


              <div className="mood-options">

                {[
                  ["Happy", "😊"],
                  ["Sad", "😢"],
                  ["Romantic", "❤️"],
                  ["Excited", "🔥"],
                  ["Chill", "😎"],
                  ["Thrilled", "😱"],
                  ["Thoughtful", "🧠"],
                  ["Funny", "😂"]
                ].map(([name, emoji]) => (

                  <button
                    type="button"
                    key={name}
                    className={
                      mood === name
                        ? "mood-option active"
                        : "mood-option"
                    }
                    onClick={() =>
                      setMood(
                        mood === name
                          ? ""
                          : name
                      )
                    }
                  >

                    <span>
                      {emoji}
                    </span>

                    {name}

                  </button>

                ))}

              </div>

            </div>


            <div className="filter-grid">

              <div className="filter-group">

                <label>
                  🎭 Genre
                </label>

                <select
                  value={genre}
                  onChange={e =>
                    setGenre(e.target.value)
                  }
                >

                  <option value="">
                    Any Genre
                  </option>

                  <option value="Action">
                    Action
                  </option>

                  <option value="Adventure">
                    Adventure
                  </option>

                  <option value="Animation">
                    Animation
                  </option>

                  <option value="Comedy">
                    Comedy
                  </option>

                  <option value="Crime">
                    Crime
                  </option>

                  <option value="Drama">
                    Drama
                  </option>

                  <option value="Horror">
                    Horror
                  </option>

                  <option value="Mystery">
                    Mystery
                  </option>

                  <option value="Romance">
                    Romance
                  </option>

                  <option value="Science Fiction">
                    Science Fiction
                  </option>

                  <option value="Thriller">
                    Thriller
                  </option>

                  <option value="Family">
                    Family
                  </option>

                  <option value="Fantasy">
                    Fantasy
                  </option>

                </select>

              </div>


              <div className="filter-group">

                <label>
                  ⭐ Minimum Rating
                </label>

                <select
                  value={rating}
                  onChange={e =>
                    setRating(e.target.value)
                  }
                >

                  <option value="">
                    Any Rating
                  </option>

                  <option value="6">
                    6.0+
                  </option>

                  <option value="7">
                    7.0+
                  </option>

                  <option value="8">
                    8.0+
                  </option>

                  <option value="9">
                    9.0+
                  </option>

                </select>

              </div>


              <div className="filter-group">

                <label>
                  🌐 Language
                </label>

                <select
                  value={language}
                  onChange={e =>
                    setLanguage(e.target.value)
                  }
                >

                  <option value="">
                    Any Language
                  </option>

                  <option value="English">
                    English
                  </option>

                  <option value="Hindi">
                    Hindi
                  </option>

                  <option value="Spanish">
                    Spanish
                  </option>

                  <option value="Japanese">
                    Japanese
                  </option>

                  <option value="Korean">
                    Korean
                  </option>

                  <option value="French">
                    French
                  </option>

                  <option value="German">
                    German
                  </option>

                  <option value="Italian">
                    Italian
                  </option>

                  <option value="Chinese">
                    Chinese
                  </option>

                  <option value="Russian">
                    Russian
                  </option>

                  <option value="Portuguese">
                    Portuguese
                  </option>

                  <option value="Arabic">
                    Arabic
                  </option>

                  <option value="Telugu">
                    Telugu
                  </option>

                  <option value="Tamil">
                    Tamil
                  </option>

                  <option value="Malayalam">
                    Malayalam
                  </option>

                </select>

              </div>


              <div className="filter-group">

                <label>
                  📅 Release Year
                </label>

                <div className="year-inputs">

                  <input
                    type="number"
                    placeholder="From"
                    value={yearFrom}
                    onChange={e =>
                      setYearFrom(e.target.value)
                    }
                  />

                  <span>—</span>

                  <input
                    type="number"
                    placeholder="To"
                    value={yearTo}
                    onChange={e =>
                      setYearTo(e.target.value)
                    }
                  />

                </div>

              </div>

            </div>


            <div className="finder-actions">

              <button
                type="button"
                className="find-button"
                onClick={() => {
                  setExcludedMovies([]);
                  findMovie(false);
                }}
                disabled={discoverLoading}
              >

                {discoverLoading
                  ? "Finding..."
                  : "🎬 Find Movie"}

              </button>


              <button
                type="button"
                className="clear-button"
                onClick={clearFilters}
              >
                Clear Filters
              </button>

            </div>

          </div>


          {discoverError && (

            <div className="discover-error">
              {discoverError}
            </div>

          )}


          {discoverMovie && (

            <div
              className="discover-result"
              id="discover-result"
            >

              <div className="discover-poster">

                {discoverMovie.poster_url ? (

                  <img
                    src={discoverMovie.poster_url}
                    alt={discoverMovie.title}
                  />

                ) : (

                  <div className="large-no-poster">
                    🎬
                  </div>

                )}

              </div>


              <div className="discover-details">

                <div className="picked-label">
                  ✨ YOUR MOVIE
                </div>


                <h2>
                  {discoverMovie.title}
                </h2>


                <div className="discover-meta">

                  {discoverMovie.rating > 0 && (

                    <span>
                      ⭐{" "}
                      {Number(
                        discoverMovie.rating
                      ).toFixed(1)}
                    </span>

                  )}

                  {discoverMovie.year && (

                    <span>
                      📅 {discoverMovie.year}
                    </span>

                  )}

                  {discoverMovie.runtime > 0 && (

                    <span>
                      ⏱ {discoverMovie.runtime} min
                    </span>

                  )}

                </div>


                {discoverMovie.genres && (

                  <div className="discover-detail">

                    <strong>
                      🎭 Genres
                    </strong>

                    <span>
                      {discoverMovie.genres}
                    </span>

                  </div>

                )}


                {discoverMovie.language && (

                  <div className="discover-detail">

                    <strong>
                      🌐 Language
                    </strong>

                    <span>
                      {discoverMovie.language}
                    </span>

                  </div>

                )}


                {discoverMovie.director && (

                  <div className="discover-detail">

                    <strong>
                      🎬 Director
                    </strong>

                    <span>
                      {discoverMovie.director}
                    </span>

                  </div>

                )}


                {discoverMovie.cast && (

                  <div className="discover-detail">

                    <strong>
                      👥 Cast
                    </strong>

                    <span>
                      {discoverMovie.cast}
                    </span>

                  </div>

                )}


                {discoverMovie.release_date && (

                  <div className="discover-detail">

                    <strong>
                      📅 Release Date
                    </strong>

                    <span>
                      {discoverMovie.release_date}
                    </span>

                  </div>

                )}


                {discoverMovie.overview && (

                  <div className="discover-overview">

                    <h3>
                      Overview
                    </h3>

                    <p>
                      {discoverMovie.overview}
                    </p>

                  </div>

                )}


                <button
                  type="button"
                  className="regenerate-button"
                  onClick={() =>
                    findMovie(true)
                  }
                  disabled={discoverLoading}
                >

                  🔄{" "}
                  {discoverLoading
                    ? "Finding..."
                    : "Regenerate"}

                </button>

              </div>

            </div>

          )}

        </section>


        <section
          className="content-section top-rated-section"
          id="top-rated"
        >

          <div className="section-heading">

            <p>
              POPULAR PICKS
            </p>

            <h2>
              ⭐ Top Rated Movies
            </h2>

            <span>
              Highly rated movies from our
              collection
            </span>

          </div>


          <div className="movie-grid">

            {topRated.map(movie => (

              <MovieCard
                key={movie.id}
                movie={movie}
              />

            ))}

          </div>

        </section>

      </main>


      <footer>

        <div className="footer-logo">
          🎬 MovieVerse
        </div>

        <p>
          Discover. Explore. Enjoy.
        </p>

        <small>
          MovieVerse • AI-Powered Movie
          Recommendation System
        </small>

      </footer>

    </div>
  );
}

export default App;