
import MovieCard from "./Moviecard.jsx";

function Relatedmovies({
  selectedMovie,
  recommendations,
  selectMovie
}) {
  return (
    selectedMovie &&
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
              selectMovie={selectMovie}
            />
          ))}
        </div>
      </section>
    )
  );
}

export default Relatedmovies;
