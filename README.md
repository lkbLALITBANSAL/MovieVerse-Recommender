# 🎬 MovieVerse – Movie Recommendation System

MovieVerse is a full-stack movie recommendation web application that helps users discover movies based on their interests.

The application combines a machine-learning recommendation system with a modern React frontend and FastAPI backend to provide movie search, detailed information, similar movie recommendations, and top-rated movies.

---

## 🚀 Live Demo

🌐 **MovieVerse:**  
https://movie-verse-recommender.vercel.app/

---

## ✨ Features

- 🔎 Search movies by title
- 🎬 View detailed information about a movie
- ⭐ Movie ratings
- 📅 Release year and release date
- ⏱️ Movie runtime
- 🎭 Genres
- 📝 Movie overview
- 🎥 Cast and director information
- 🖼️ Movie posters
- 🤖 ML-based movie recommendations
- 🔗 Related movie recommendations
- 🏆 Top-rated movies section
- 🌙 Dark-themed responsive UI
- ⚡ Fast API-based communication
- 🔄 Movie data is regularly updated to keep the database fresh

---

## 🧠 Recommendation System

MovieVerse uses **Sentence-BERT (SBERT)** to understand the semantic meaning of movie information and generate meaningful movie recommendations.

Movie information such as:

- Movie overview
- Genres
- Keywords
- Cast
- Director

is combined to create a textual representation of each movie.

SBERT converts these movie descriptions into numerical vectors called **embeddings**.

The similarity between movies is then calculated using their embeddings.

### Recommendation Flow

```text
Movie Information
       ↓
Text Preprocessing
       ↓
Combined Movie Features
       ↓
SBERT
       ↓
Movie Embeddings
       ↓
Similarity Calculation
       ↓
Similar Movies
       ↓
Recommended Movies
