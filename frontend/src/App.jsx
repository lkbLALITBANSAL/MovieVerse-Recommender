import { useEffect, useState } from "react";
import Navbar from "./components/Navbar.jsx";
import HeroSearch from "./components/Herosearch.jsx";
import MovieDetails from "./components/Moviedetails.jsx";
import RelatedMovies from "./components/Relatedmovies.jsx";
import MovieFinder from "./components/MovieFinder.jsx";
import DiscoverResult from "./components/Discoverresult.jsx";
import TopRatedMovies from "./components/TopRatedMovies.jsx";
import Footer from "./components/Footer.jsx";

import {
  searchMovies,
  getMovie,
  getRecommendations,
  discoverMovies
} from "./api";

import "./styles.css";

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

  // PRELOAD TOP-RATED POSTERS
  function preloadImages(movies) {
    movies.slice(0, 12).forEach((movie) => {
      if (movie?.poster_url) {
        const img = new Image();
        img.src = movie.poster_url;
      }
    });
  }

  // LOAD TOP-RATED MOVIES FROM LOCAL JSON
  useEffect(() => {
    loadTopRated();
  }, []);

  async function loadTopRated() {
    try {
      const response = await fetch("/top_rated.json");

      if (!response.ok) {
        throw new Error("Unable to load top-rated movies JSON");
      }

      const data = await response.json();

      setTopRated(Array.isArray(data) ? data : []);
      preloadImages(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Top-rated movies loading error:", err);
      setTopRated([]);
    }
  }

  // SEARCH SUGGESTIONS
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

  // SELECT MOVIE
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

  // SEARCH
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

  // FIND MOVIE BY MOOD
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
        (movie) => !excludedMovies.includes(String(movie.id))
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

      setExcludedMovies((prev) => {
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

  // CLEAR FILTERS
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

  // SCROLL TO FINDER
  function scrollToFinder() {
    document
      .getElementById("movie-finder")
      ?.scrollIntoView({
        behavior: "smooth"
      });
  }

  // UI
  return (
    <div className="app">
      <Navbar scrollToFinder={scrollToFinder} />

      <main>
        <HeroSearch
          query={query}
          setQuery={setQuery}
          suggestions={suggestions}
          handleSearch={handleSearch}
          selectMovie={selectMovie}
          scrollToFinder={scrollToFinder}
        />

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
          <MovieDetails selectedMovie={selectedMovie} />
        )}

        <RelatedMovies
          selectedMovie={selectedMovie}
          recommendations={recommendations}
          selectMovie={selectMovie}
        />

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
                <span>{" "}for Your Mood</span>
              </h2>

              <p>
                Tell us what you're in the mood
                for and we'll pick one movie
                from our collection.
              </p>
            </div>
          </div>

          <MovieFinder
            mood={mood}
            setMood={setMood}
            genre={genre}
            setGenre={setGenre}
            rating={rating}
            setRating={setRating}
            language={language}
            setLanguage={setLanguage}
            yearFrom={yearFrom}
            setYearFrom={setYearFrom}
            yearTo={yearTo}
            setYearTo={setYearTo}
            findMovie={findMovie}
            clearFilters={clearFilters}
            discoverLoading={discoverLoading}
            setExcludedMovies={setExcludedMovies}
          />

          {discoverError && (
            <div className="discover-error">
              {discoverError}
            </div>
          )}

          <DiscoverResult
            discoverMovie={discoverMovie}
            findMovie={findMovie}
            discoverLoading={discoverLoading}
          />
        </section>

        <TopRatedMovies
          topRated={topRated}
          selectMovie={selectMovie}
        />
      </main>

      <Footer />
    </div>
  );
}

export default App;