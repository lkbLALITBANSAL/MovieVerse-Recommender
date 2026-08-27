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


export function discoverMovies(filters) {

  const params =
    new URLSearchParams();

  if (filters.mood) {
    params.append(
      "mood",
      filters.mood
    );
  }

  if (filters.genre) {
    params.append(
      "genre",
      filters.genre
    );
  }

  if (filters.rating) {
    params.append(
      "rating",
      filters.rating
    );
  }

  if (filters.language) {
    params.append(
      "language",
      filters.language
    );
  }

  if (filters.yearFrom) {
    params.append(
      "year_from",
      filters.yearFrom
    );
  }

  if (filters.yearTo) {
    params.append(
      "year_to",
      filters.yearTo
    );
  }

  if (
    filters.exclude &&
    filters.exclude.length
  ) {

    params.append(
      "exclude",
      filters.exclude.join(",")
    );

  }

  return request(
    `/discover?${params.toString()}`
  );

}