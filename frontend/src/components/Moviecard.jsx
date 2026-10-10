function MovieCard({
  movie,
  priority = false,
  selectMovie,
}) {
  return (
    <div
      className="movie-card"
      onClick={() => selectMovie(movie)}
    >
      {movie.poster_url ? (
        <img
          src={movie.poster_url}
          alt={movie.title}
          loading={priority ? "eager" : "lazy"}
          decoding="async"
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

export default MovieCard;