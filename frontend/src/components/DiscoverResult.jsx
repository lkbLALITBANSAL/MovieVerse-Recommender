
function Discoverresult({
  discoverMovie,
  findMovie,
  discoverLoading,
}) {
  if (!discoverMovie) return null;

  return (
    <div className="discover-result" id="discover-result">
      <div className="discover-poster">
        {discoverMovie.poster_url ? (
          <img
            src={discoverMovie.poster_url}
            alt={discoverMovie.title}
            loading="eager"
            decoding="async"
          />
        ) : (
          <div className="large-no-poster">🎬</div>
        )}
      </div>

      <div className="discover-details">
        <div className="picked-label">✨ YOUR MOVIE</div>

        <h2>{discoverMovie.title}</h2>

        <div className="discover-meta">
          {discoverMovie.rating > 0 && (
            <span>
              ⭐{" "}{Number(discoverMovie.rating).toFixed(1)}
            </span>
          )}

          {discoverMovie.year && (
            <span>📅 {discoverMovie.year}</span>
          )}

          {discoverMovie.runtime > 0 && (
            <span>⏱ {discoverMovie.runtime} min</span>
          )}
        </div>

        {discoverMovie.genres && (
          <div className="discover-detail">
            <strong>🎭 Genres</strong>
            <span>{discoverMovie.genres}</span>
          </div>
        )}

        {discoverMovie.language && (
          <div className="discover-detail">
            <strong>🌐 Language</strong>
            <span>{discoverMovie.language}</span>
          </div>
        )}

        {discoverMovie.director && (
          <div className="discover-detail">
            <strong>🎬 Director</strong>
            <span>{discoverMovie.director}</span>
          </div>
        )}

        {discoverMovie.cast && (
          <div className="discover-detail">
            <strong>👥 Cast</strong>
            <span>{discoverMovie.cast}</span>
          </div>
        )}

        {discoverMovie.release_date && (
          <div className="discover-detail">
            <strong>📅 Release Date</strong>
            <span>{discoverMovie.release_date}</span>
          </div>
        )}

        {discoverMovie.overview && (
          <div className="discover-overview">
            <h3>Overview</h3>
            <p>{discoverMovie.overview}</p>
          </div>
        )}

        <button
          type="button"
          className="regenerate-button"
          onClick={() => findMovie(true)}
          disabled={discoverLoading}
        >
          🔄{" "}
          {discoverLoading ? "Finding..." : "Regenerate"}
        </button>
      </div>
    </div>
  );
}

export default Discoverresult;
