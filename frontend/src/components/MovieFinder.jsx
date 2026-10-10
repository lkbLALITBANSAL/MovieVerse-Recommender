
function MovieFinder({
  mood,
  setMood,
  genre,
  setGenre,
  rating,
  setRating,
  language,
  setLanguage,
  yearFrom,
  setYearFrom,
  yearTo,
  setYearTo,
  findMovie,
  clearFilters,
  discoverLoading
}) {
  return (
    <div className="finder-box">
      {/* MOOD */}
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
                  mood === name ? "" : name
                )
              }
            >
              <span>{emoji}</span>
              {name}
            </button>
          ))}
        </div>
      </div>

      {/* FILTER GRID */}
      <div className="filter-grid">
        {/* GENRE */}
        <div className="filter-group">
          <label>🎭 Genre</label>

          <select
            value={genre}
            onChange={e => setGenre(e.target.value)}
          >
            <option value="">Any Genre</option>
            <option value="Action">Action</option>
            <option value="Adventure">Adventure</option>
            <option value="Animation">Animation</option>
            <option value="Comedy">Comedy</option>
            <option value="Crime">Crime</option>
            <option value="Drama">Drama</option>
            <option value="Horror">Horror</option>
            <option value="Mystery">Mystery</option>
            <option value="Romance">Romance</option>
            <option value="Science Fiction">Science Fiction</option>
            <option value="Thriller">Thriller</option>
            <option value="Family">Family</option>
            <option value="Fantasy">Fantasy</option>
          </select>
        </div>

        {/* RATING */}
        <div className="filter-group">
          <label>⭐ Minimum Rating</label>

          <select
            value={rating}
            onChange={e => setRating(e.target.value)}
          >
            <option value="">Any Rating</option>
            <option value="6">6.0+</option>
            <option value="7">7.0+</option>
            <option value="8">8.0+</option>
            <option value="9">9.0+</option>
          </select>
        </div>

        {/* LANGUAGE */}
        <div className="filter-group">
          <label>🌐 Language</label>

          <select
            value={language}
            onChange={e => setLanguage(e.target.value)}
          >
            <option value="">Any Language</option>
            <option value="English">English</option>
            <option value="Hindi">Hindi</option>
            <option value="Spanish">Spanish</option>
            <option value="Japanese">Japanese</option>
            <option value="Korean">Korean</option>
            <option value="French">French</option>
            <option value="German">German</option>
            <option value="Italian">Italian</option>
            <option value="Chinese">Chinese</option>
            <option value="Russian">Russian</option>
            <option value="Portuguese">Portuguese</option>
            <option value="Arabic">Arabic</option>
            <option value="Telugu">Telugu</option>
            <option value="Tamil">Tamil</option>
            <option value="Malayalam">Malayalam</option>
          </select>
        </div>

        {/* YEAR */}
        <div className="filter-group">
          <label>📅 Release Year</label>

          <div className="year-inputs">
            <input
              type="number"
              placeholder="From"
              value={yearFrom}
              onChange={e => setYearFrom(e.target.value)}
            />

            <span>—</span>

            <input
              type="number"
              placeholder="To"
              value={yearTo}
              onChange={e => setYearTo(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* ACTIONS */}
      <div className="finder-actions">
        <button
          type="button"
          className="find-button"
          onClick={() => {
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
  );
}

export default MovieFinder;
