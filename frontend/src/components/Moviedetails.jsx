
function MovieDetails({ selectedMovie }) {
  return (
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
              loading="eager"
              decoding="async"
            />
          ) : (
            <div className="large-no-poster">
              🎬
            </div>
          )}
        </div>

        <div className="movie-info">
          <h1>{selectedMovie.title}</h1>

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
              <strong>Genres</strong>
              <span>{selectedMovie.genres}</span>
            </div>
          )}

          {selectedMovie.language && (
            <div className="detail-row">
              <strong>Language</strong>
              <span>{selectedMovie.language}</span>
            </div>
          )}

          {selectedMovie.director && (
            <div className="detail-row">
              <strong>Director</strong>
              <span>{selectedMovie.director}</span>
            </div>
          )}

          {selectedMovie.cast && (
            <div className="detail-row">
              <strong>Cast</strong>
              <span>{selectedMovie.cast}</span>
            </div>
          )}

          {selectedMovie.overview && (
            <div className="overview">
              <h3>Overview</h3>
              <p>{selectedMovie.overview}</p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

export default MovieDetails;
