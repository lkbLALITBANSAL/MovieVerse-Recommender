// frontend/src/api.js

const API_BASE =
  import.meta.env.VITE_API_URL ||
  "http://localhost:8000";


async function request(path) {

  const response =
    await fetch(
      `${API_BASE}${path}`
    );

  if (!response.ok) {

    throw new Error(
      `Request failed: ${response.status}`
    );

  }

  return response.json();

}


export function searchMovies(query) {

  return request(
    `/search?q=${encodeURIComponent(query)}`
  );

}


export function getMovie(id) {

  return request(
    `/movies/${encodeURIComponent(id)}`
  );

}


export function getRecommendations(
  id,
  limit = 8
) {

  return request(
    `/recommend/${encodeURIComponent(id)}?limit=${limit}`
  );

}


export function getTopRated(
  limit = 10
) {

  return request(
    `/top-rated?limit=${limit}`
  );

}