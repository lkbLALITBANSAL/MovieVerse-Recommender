
function HeroSearch({
  query,
  setQuery,
  suggestions,
  handleSearch,
  selectMovie,
  scrollToFinder
}) {
  return (
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

          {/* SEARCH SUGGESTIONS */}
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
                        loading="lazy"
                        decoding="async"
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
  );
}

export default HeroSearch;
