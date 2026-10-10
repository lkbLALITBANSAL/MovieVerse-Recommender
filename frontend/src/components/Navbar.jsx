function Navbar({ scrollToFinder }) {
  return (
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
  );
}

export default Navbar;