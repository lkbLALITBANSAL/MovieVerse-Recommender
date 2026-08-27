// frontend/src/App.jsx

import { useEffect, useRef, useState } from "react";

import {
  ArrowRight,
  ChevronLeft,
  ChevronRight,
  Clock3,
  Film,
  Moon,
  Play,
  Search,
  Star,
  Sun,
  UserRound,
  X
} from "lucide-react";

import {
  getMovie,
  getRecommendations,
  getTopRated,
  searchMovies
} from "./api";


const fallbackPoster =
  "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=700&q=80";


function posterUrl(movie) {

  return (
    movie?.poster_url ||
    movie?.poster ||
    fallbackPoster
  );

}


function genresText(movie) {

  if (!movie?.genres) {
    return "";
  }

  if (Array.isArray(movie.genres)) {
    return movie.genres.join(", ");
  }

  return String(movie.genres)
    .replace(/^\[|\]$/g, "")
    .split(",")
    .map(x =>
      x.trim().replace(/^['"]|['"]$/g, "")
    )
    .filter(Boolean)
    .join(", ");

}


function MovieCard({
  movie,
  onClick
}) {

  return (

    <button
      className="movie-card"
      onClick={() => onClick(movie)}
    >

      <div className="poster-wrap">

        <img
          src={posterUrl(movie)}
          alt={movie.title}
          loading="lazy"
        />

        <div className="card-rating">

          <Star
            size={13}
            fill="currentColor"
          />

          {Number(
            movie.rating || 0
          ).toFixed(1)}

        </div>

      </div>

      <div className="card-info">

        <h3>
          {movie.title}
        </h3>

        <div className="card-meta">

          <span>
            {movie.year || "—"}
          </span>

          {genresText(movie) && (

            <span>
              {genresText(movie)}
            </span>

          )}

        </div>

      </div>

    </button>

  );

}


function Section({
  title,
  movies,
  onMovieClick,
  subtitle
}) {

  const row = useRef(null);

  function scroll(direction) {

    row.current?.scrollBy({
      left: direction * 650,
      behavior: "smooth"
    });

  }

  if (!movies?.length) {
    return null;
  }

  return (

    <section className="movie-section">

      <div className="section-heading">

        <div>

          <h2>
            {title}
          </h2>

          {subtitle && (
            <p>
              {subtitle}
            </p>
          )}

        </div>

        <div className="slider-buttons">

          <button
            onClick={() =>
              scroll(-1)
            }
          >
            <ChevronLeft size={19} />
          </button>

          <button
            onClick={() =>
              scroll(1)
            }
          >
            <ChevronRight size={19} />
          </button>

        </div>

      </div>

      <div
        className="movie-row"
        ref={row}
      >

        {movies.map(movie => (

          <MovieCard
            key={movie.id}
            movie={movie}
            onClick={onMovieClick}
          />

        ))}

      </div>

    </section>

  );

}


function App() {

  const [query, setQuery] =
    useState("");

  const [suggestions, setSuggestions] =
    useState([]);

  const [selected, setSelected] =
    useState(null);

  const [related, setRelated] =
    useState([]);

  const [topRated, setTopRated] =
    useState([]);

  const [loading, setLoading] =
    useState(false);

  const [searching, setSearching] =
    useState(false);

  const [dark, setDark] =
    useState(true);

  const [error, setError] =
    useState("");


  useEffect(() => {

    getTopRated(10)
      .then(setTopRated)
      .catch(() =>
        setError(
          "Backend is not running. Start the FastAPI server."
        )
      );

  }, []);


  useEffect(() => {

    const value =
      query.trim();

    if (!value) {

      setSuggestions([]);

      return;

    }

    const timer =
      setTimeout(() => {

        setSearching(true);

        searchMovies(value)
          .then(setSuggestions)
          .catch(() =>
            setSuggestions([])
          )
          .finally(() =>
            setSearching(false)
          );

      }, 180);

    return () =>
      clearTimeout(timer);

  }, [query]);


  async function selectMovie(movie) {

    setQuery(movie.title);

    setSuggestions([]);

    setLoading(true);

    setError("");

    try {

      const fullMovie =
        await getMovie(movie.id);

      const recommendations =
        await getRecommendations(
          movie.id,
          8
        );

      setSelected(fullMovie);

      setRelated(
        recommendations
      );

      window.scrollTo({
        top: 0,
        behavior: "smooth"
      });

    } catch {

      setError(
        "Could not load this movie."
      );

    } finally {

      setLoading(false);

    }

  }


  function clearSearch() {

    setQuery("");

    setSuggestions([]);

  }


  function scrollToTopRated() {

    document
      .getElementById("top-rated")
      ?.scrollIntoView({
        behavior: "smooth"
      });

  }


  return (

    <div
      className={
        dark
          ? "app"
          : "app light"
      }
    >

      <header className="navbar">

        <div className="nav-left">

          <button
            className="brand"
            onClick={() =>
              window.scrollTo({
                top: 0,
                behavior: "smooth"
              })
            }
          >
            Movie<span>Verse</span>
          </button>

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

            <button
              onClick={scrollToTopRated}
            >
              Movies
            </button>

            <button
              onClick={scrollToTopRated}
            >
              Top Rated
            </button>

            <button>
              About
            </button>

          </nav>

        </div>

        <div className="nav-right">

          <button
            className="icon-button"
            onClick={() =>
              setDark(!dark)
            }
          >

            {dark ? (
              <Moon size={19} />
            ) : (
              <Sun size={19} />
            )}

          </button>

          <button className="profile-button">
            <UserRound size={18} />
          </button>

        </div>

      </header>


      <main>

        <section className="search-area">

          <div className="search-box">

            <Search size={21} />

            <input
              value={query}
              onChange={(e) =>
                setQuery(e.target.value)
              }
              placeholder="Search movies..."
              autoComplete="off"
            />

            {query && (

              <button
                className="clear-button"
                onClick={clearSearch}
              >
                <X size={17} />
              </button>

            )}

          </div>


          {query && (

            <div className="suggestions">

              {searching && (

                <div className="suggestion-message">
                  Searching...
                </div>

              )}


              {!searching &&
                suggestions.length === 0 && (

                  <div className="suggestion-message">
                    No movies found
                  </div>

                )}


              {!searching &&
                suggestions
                  .slice(0, 6)
                  .map(movie => (

                    <button
                      className="suggestion"
                      key={movie.id}
                      onClick={() =>
                        selectMovie(movie)
                      }
                    >

                      <img
                        src={posterUrl(movie)}
                        alt=""
                      />

                      <div>

                        <strong>
                          {movie.title}
                        </strong>

                        <span>
                          {movie.year || "—"}

                          {movie.language &&
                            ` • ${movie.language.toUpperCase()}`}
                        </span>

                      </div>

                      <div className="suggestion-rating">

                        <Star
                          size={13}
                          fill="currentColor"
                        />

                        {Number(
                          movie.rating || 0
                        ).toFixed(1)}

                      </div>

                    </button>

                  ))}


              {!searching &&
                suggestions.length > 0 && (

                  <div className="all-results">

                    View results for "{query}"

                    <ArrowRight
                      size={17}
                    />

                  </div>

                )}

            </div>

          )}

        </section>


        {error && (

          <div className="error-banner">
            {error}
          </div>

        )}


        {loading ? (

          <div className="loading">

            <div className="spinner" />

            <p>
              Finding your movie...
            </p>

          </div>

        ) : selected ? (

          <>

            <section className="hero">

              <div className="hero-poster">

                <img
                  src={posterUrl(selected)}
                  alt={selected.title}
                />

              </div>


              <div className="hero-content">

                <div className="eyebrow">
                  MOVIEVERSE PICK
                </div>

                <h1>
                  {selected.title}
                </h1>


                <div className="chips">

                  {selected.year && (
                    <span>
                      {selected.year}
                    </span>
                  )}

                  {selected.runtime > 0 && (

                    <span>
                      {Math.floor(
                        selected.runtime / 60
                      )}
                      h{" "}
                      {selected.runtime % 60}
                      m
                    </span>

                  )}

                  {genresText(selected) && (

                    <span>
                      {genresText(selected)}
                    </span>

                  )}

                </div>


                <div className="rating-line">

                  <Star
                    size={19}
                    fill="currentColor"
                  />

                  <b>
                    {Number(
                      selected.rating || 0
                    ).toFixed(1)}
                  </b>

                  <span>
                    /10
                  </span>

                </div>


                <p className="overview">

                  {selected.overview ||
                    "No overview is available for this movie."}

                </p>


                <div className="details-grid">

                  {selected.director && (

                    <div>

                      <label>
                        Director
                      </label>

                      <span>
                        {selected.director}
                      </span>

                    </div>

                  )}


                  {selected.cast && (

                    <div>

                      <label>
                        Cast
                      </label>

                      <span>
                        {selected.cast}
                      </span>

                    </div>

                  )}


                  {selected.language && (

                    <div>

                      <label>
                        Language
                      </label>

                      <span>
                        {selected.language.toUpperCase()}
                      </span>

                    </div>

                  )}


                  {selected.release_date && (

                    <div>

                      <label>
                        Release Date
                      </label>

                      <span>
                        {selected.release_date}
                      </span>

                    </div>

                  )}


                  {genresText(selected) && (

                    <div>

                      <label>
                        Genres
                      </label>

                      <span>
                        {genresText(selected)}
                      </span>

                    </div>

                  )}

                </div>


                <div className="hero-actions">

                  <button className="primary-button">

                    <Play
                      size={17}
                      fill="currentColor"
                    />

                    Watch Trailer

                  </button>

                  <button className="secondary-button">

                    ＋ Add to Watchlist

                  </button>

                </div>

              </div>


              <aside className="quick-info">

                <div className="info-item">

                  <Star size={21} />

                  <div>

                    <label>
                      Rating
                    </label>

                    <strong>
                      {Number(
                        selected.rating || 0
                      ).toFixed(1)}
                      /10
                    </strong>

                  </div>

                </div>


                <div className="info-item">

                  <Clock3 size={21} />

                  <div>

                    <label>
                      Runtime
                    </label>

                    <strong>
                      {selected.runtime
                        ? `${selected.runtime} min`
                        : "—"}
                    </strong>

                  </div>

                </div>


                <div className="info-item">

                  <Film size={21} />

                  <div>

                    <label>
                      Genres
                    </label>

                    <strong>
                      {genresText(selected) ||
                        "—"}
                    </strong>

                  </div>

                </div>


                <div className="info-item">

                  <div className="status-dot" />

                  <div>

                    <label>
                      Status
                    </label>

                    <strong>
                      Available
                    </strong>

                  </div>

                </div>

              </aside>

            </section>


            <Section
              title="Related Movies"
              subtitle="Recommended using your SBERT content-similarity model"
              movies={related}
              onMovieClick={selectMovie}
            />

          </>

        ) : (

          <section className="empty-hero">

            <div className="empty-icon">

              <Film size={32} />

            </div>

            <h1>
              Discover your next movie
            </h1>

            <p>
              Search a movie above and
              MovieVerse will find related
              movies using semantic similarity.
            </p>

          </section>

        )}


        <section id="top-rated">

          <Section
            title="Top Rated Movies"
            subtitle="Always shown on the MovieVerse home page"
            movies={topRated}
            onMovieClick={selectMovie}
          />

        </section>

      </main>


      <footer>

        <div className="footer-brand">
          Movie<span>Verse</span>
        </div>

        <p>
          Discover. Explore. Watch.
        </p>

      </footer>

    </div>

  );

}

export default App;