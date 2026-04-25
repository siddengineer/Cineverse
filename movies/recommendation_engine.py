# """
# CineVerse Recommendation Engine
# - Content-based filtering: TF-IDF on genres + overview
# - User-based filtering: ratings + watchlist + experience feelings
# Fully dataset-driven. No external API calls.
# """
# import logging
# import numpy as np
# from django.core.cache import cache
# from django.db.models import Avg, Count

# logger = logging.getLogger(__name__)


# def _get_tfidf_matrix():
#     """Build or retrieve cached TF-IDF matrix over all movies."""
#     from .models import Movie
#     cache_key = 'tfidf_matrix_v2'
#     cached = cache.get(cache_key)
#     if cached:
#         return cached['matrix'], cached['movie_ids']

#     try:
#         from sklearn.feature_extraction.text import TfidfVectorizer
#         from sklearn.metrics.pairwise import cosine_similarity

#         movies = list(Movie.objects.only('id', 'genre_names', 'overview', 'language').order_by('id'))
#         movie_ids = [m.id for m in movies]

#         corpus = []
#         for m in movies:
#             text = ' '.join([
#                 (m.genre_names or '') * 3,   # weight genres 3x
#                 m.overview or '',
#                 (m.language or '') * 2,
#             ])
#             corpus.append(text.strip() or 'unknown')

#         vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
#         matrix = vectorizer.fit_transform(corpus)

#         result = {'matrix': matrix, 'movie_ids': movie_ids}
#         cache.set(cache_key, result, timeout=3600 * 12)  # 12 hours
#         return matrix, movie_ids

#     except Exception as e:
#         logger.error(f"TF-IDF build failed: {e}")
#         return None, []


# def get_content_recommendations(movie, n=10):
#     """
#     Content-based: find movies similar to given movie
#     using genre + overview TF-IDF cosine similarity.
#     """
#     from .models import Movie
#     from sklearn.metrics.pairwise import cosine_similarity

#     try:
#         matrix, movie_ids = _get_tfidf_matrix()
#         if matrix is None or movie.id not in movie_ids:
#             return _fallback_recommendations(movie, n)

#         idx = movie_ids.index(movie.id)
#         movie_vec = matrix[idx]
#         scores = cosine_similarity(movie_vec, matrix).flatten()
#         # Sort descending, skip self
#         top_indices = scores.argsort()[::-1]
#         top_movie_ids = [movie_ids[i] for i in top_indices if movie_ids[i] != movie.id][:n * 2]

#         movies = list(Movie.objects.filter(id__in=top_movie_ids))
#         # Preserve score order
#         id_score = {movie_ids[i]: scores[i] for i in top_indices}
#         movies.sort(key=lambda m: id_score.get(m.id, 0), reverse=True)
#         return movies[:n]

#     except Exception as e:
#         logger.error(f"Content recommendation failed: {e}")
#         return _fallback_recommendations(movie, n)


# def _fallback_recommendations(movie, n=10):
#     """Simple genre-based fallback if sklearn not available."""
#     from .models import Movie
#     genre_list = [g.strip() for g in (movie.genre_names or '').split(',') if g.strip()]
#     if genre_list:
#         qs = Movie.objects.filter(genre_names__icontains=genre_list[0]).exclude(id=movie.id)
#     else:
#         qs = Movie.objects.exclude(id=movie.id)
#     return list(qs.order_by('-popularity')[:n])


# def get_user_recommendations(user, n=20):
#     """
#     User-based + content filtering:
#     1. Find user's top-rated genres from ratings + experience
#     2. Get movies in those genres user hasn't seen
#     3. Sort by weighted rating + popularity
#     """
#     from .models import Movie, UserRating, Watchlist
#     from experience.models import UserMovieExperience

#     # Gather liked genres from ratings (>=7)
#     liked_ratings = UserRating.objects.filter(user=user, rating__gte=7).select_related('movie')
#     liked_genre_names = []
#     liked_movie_ids = set()

#     for r in liked_ratings:
#         liked_movie_ids.add(r.movie.id)
#         for g in (r.movie.genre_names or '').split(','):
#             g = g.strip()
#             if g:
#                 liked_genre_names.append(g)

#     # Also pull from experiences with positive feelings
#     positive_feelings = ['amazing', 'loved', 'great', 'emotional', 'brilliant', 'masterpiece', 'enjoyed']
#     experiences = UserMovieExperience.objects.filter(
#         user=user
#     ).select_related('movie')

#     for exp in experiences:
#         liked_movie_ids.add(exp.movie_id)
#         feeling = (exp.feeling or '').lower()
#         if any(pf in feeling for pf in positive_feelings) or (exp.rating and exp.rating >= 7):
#             for g in (exp.movie.genre_names or '').split(','):
#                 g = g.strip()
#                 if g:
#                     liked_genre_names.append(g)

#     # Watchlist genres
#     watchlist = Watchlist.objects.filter(user=user).select_related('movie')
#     for w in watchlist:
#         liked_movie_ids.add(w.movie.id)

#     if not liked_genre_names:
#         # Cold start: return popular movies
#         return list(Movie.objects.order_by('-popularity', '-rating')[:n])

#     # Find most common genres
#     from collections import Counter
#     genre_counts = Counter(liked_genre_names)
#     top_genres = [g for g, _ in genre_counts.most_common(5)]

#     # Build query for movies matching any top genre
#     from django.db.models import Q
#     q = Q()
#     for genre in top_genres:
#         q |= Q(genre_names__icontains=genre)

#     candidates = Movie.objects.filter(q).exclude(id__in=liked_movie_ids).order_by('-rating', '-popularity')
#     return list(candidates[:n])




"""
CineVerse Recommendation Engine (Lightweight Version)
- No numpy
- No sklearn
- Pure Python TF + cosine-like similarity
"""

import logging
from collections import Counter
from django.core.cache import cache

logger = logging.getLogger(__name__)


# ---------------- TEXT PROCESSING ----------------

def _tokenize(text):
    if not text:
        return []
    return text.lower().split()


def _build_vector(text):
    tokens = _tokenize(text)
    return Counter(tokens)


def _cosine_sim(vec1, vec2):
    # dot product
    common = set(vec1.keys()) & set(vec2.keys())
    dot = sum(vec1[w] * vec2[w] for w in common)

    # magnitude
    mag1 = sum(v ** 2 for v in vec1.values()) ** 0.5
    mag2 = sum(v ** 2 for v in vec2.values()) ** 0.5

    if mag1 == 0 or mag2 == 0:
        return 0

    return dot / (mag1 * mag2)


# ---------------- MATRIX BUILD ----------------

def _get_movie_vectors():
    from .models import Movie

    cache_key = "movie_vectors_v1"
    cached = cache.get(cache_key)

    if cached:
        return cached

    movies = list(Movie.objects.only('id', 'genre_names', 'overview', 'language'))
    vectors = {}
    movie_ids = []

    for m in movies:
        text = " ".join([
            (m.genre_names or "") * 3,
            m.overview or "",
            (m.language or "") * 2
        ])

        vec = _build_vector(text)
        vectors[m.id] = vec
        movie_ids.append(m.id)

    cache.set(cache_key, (vectors, movie_ids), timeout=3600 * 12)
    return vectors, movie_ids


# ---------------- CONTENT BASED ----------------

def get_content_recommendations(movie, n=10):
    from .models import Movie

    try:
        vectors, movie_ids = _get_movie_vectors()

        if movie.id not in vectors:
            return _fallback_recommendations(movie, n)

        target_vec = vectors[movie.id]

        scores = []

        for mid in movie_ids:
            if mid == movie.id:
                continue

            sim = _cosine_sim(target_vec, vectors[mid])
            if sim > 0:
                scores.append((sim, mid))

        scores.sort(reverse=True)

        top_ids = [mid for _, mid in scores[:n * 2]]

        movies = list(Movie.objects.filter(id__in=top_ids))

        score_map = dict(scores)
        movies.sort(key=lambda m: score_map.get(m.id, 0), reverse=True)

        return movies[:n]

    except Exception as e:
        logger.error(f"Recommendation failed: {e}")
        return _fallback_recommendations(movie, n)


# ---------------- FALLBACK ----------------

def _fallback_recommendations(movie, n=10):
    from .models import Movie

    genres = [g.strip() for g in (movie.genre_names or "").split(",") if g.strip()]

    if genres:
        qs = Movie.objects.filter(
            genre_names__icontains=genres[0]
        ).exclude(id=movie.id)
    else:
        qs = Movie.objects.exclude(id=movie.id)

    return list(qs.order_by('-popularity')[:n])


# ---------------- USER BASED ----------------

def get_user_recommendations(user, n=20):
    from .models import Movie, UserRating, Watchlist
    from experience.models import UserMovieExperience

    liked_genres = []
    watched_ids = set()

    ratings = UserRating.objects.filter(user=user, rating__gte=7).select_related('movie')

    for r in ratings:
        watched_ids.add(r.movie.id)
        liked_genres += (r.movie.genre_names or "").split(",")

    experiences = UserMovieExperience.objects.filter(user=user).select_related('movie')

    for exp in experiences:
        watched_ids.add(exp.movie_id)
        if (exp.rating and exp.rating >= 7) or 'good' in (exp.feeling or '').lower():
            liked_genres += (exp.movie.genre_names or "").split(",")

    watchlist = Watchlist.objects.filter(user=user).select_related('movie')

    for w in watchlist:
        watched_ids.add(w.movie.id)

    if not liked_genres:
        return list(Movie.objects.order_by('-popularity')[:n])

    from collections import Counter
    top_genres = [g for g, _ in Counter(liked_genres).most_common(5)]

    from django.db.models import Q
    q = Q()

    for g in top_genres:
        q |= Q(genre_names__icontains=g.strip())

    return list(
        Movie.objects.filter(q)
        .exclude(id__in=watched_ids)
        .order_by('-rating', '-popularity')[:n]
    )