"""
OMDb Service — ONLY used for fetching poster images.
Never used for movie lists, trending, top-rated, or any core logic.
"""
import requests
import logging
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

OMDB_BASE = 'http://www.omdbapi.com/'


def fetch_poster(movie) -> str:
    """
    Fetch poster URL for a movie from OMDb.
    Tries imdb_id first, falls back to title search.
    Returns poster URL string or empty string.
    Stores result in DB to avoid repeated API calls.
    """
    if movie.poster_fetched:
        return movie.poster_url

    if not settings.OMDB_API_KEY:
        return ''

    cache_key = f'omdb_poster_{movie.id}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    poster_url = _fetch_by_imdb_id(movie.imdb_id) if movie.imdb_id else ''

    if not poster_url and movie.title:
        poster_url = _fetch_by_title(movie.title, movie.release_year)

    # Persist to DB so we never call OMDb again for this movie
    movie.poster_url = poster_url or ''
    movie.poster_fetched = True
    movie.save(update_fields=['poster_url', 'poster_fetched'])

    cache.set(cache_key, poster_url, timeout=86400 * 7)  # cache 7 days
    return poster_url


def _fetch_by_imdb_id(imdb_id: str) -> str:
    if not imdb_id:
        return ''
    try:
        resp = requests.get(
            OMDB_BASE,
            params={'i': imdb_id, 'apikey': settings.OMDB_API_KEY},
            timeout=5
        )
        data = resp.json()
        if data.get('Response') == 'True' and data.get('Poster') not in ('N/A', None, ''):
            return data['Poster']
    except Exception as e:
        logger.warning(f"OMDb imdb_id lookup failed for {imdb_id}: {e}")
    return ''


def _fetch_by_title(title: str, year=None) -> str:
    try:
        params = {'t': title, 'apikey': settings.OMDB_API_KEY}
        if year:
            params['y'] = year
        resp = requests.get(OMDB_BASE, params=params, timeout=5)
        data = resp.json()
        if data.get('Response') == 'True' and data.get('Poster') not in ('N/A', None, ''):
            return data['Poster']
    except Exception as e:
        logger.warning(f"OMDb title lookup failed for {title}: {e}")
    return ''


def attach_posters_to_queryset(movies):
    """
    Attach posters to a list/queryset of movies.
    Only fetches from OMDb if poster not already stored.
    Returns list of movies (with poster_url set).
    """
    result = []
    for movie in movies:
        if not movie.poster_fetched or not movie.poster_url:
            fetch_poster(movie)
        result.append(movie)
    return result
