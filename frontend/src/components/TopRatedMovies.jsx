
import MovieCard from "./Moviecard.jsx";

function TopRatedMovies({ topRated, selectMovie }) {
  return (
    <section
      className="content-section top-rated-section"
      id="top-rated"
    >
      <div className="section-heading">
        <p>POPULAR PICKS</p>
        <h2>⭐ Top Rated Movies</h2>
        <span>
          Highly rated movies from our collection
        </span>
      </div>

      <div className="movie-grid">
        {topRated.map((movie, index) => (
          <MovieCard
            key={movie.id}
            movie={movie}
            priority={index < 10}
            selectMovie={selectMovie}
          />
        ))}
      </div>
    </section>
  );
}

export default TopRatedMovies;
