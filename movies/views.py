import random
import logging
from django.core.cache import cache
from django.db.models import Q
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Movie, Genre
from .serializers import MovieSerializer, MovieListSerializer, GenreSerializer
from .omdb_service import attach_posters_to_queryset
from .recommendation_engine import get_content_recommendations, get_user_recommendations

logger = logging.getLogger(__name__)


# ─── Movie Search ─────────────────────────────────────────────────────────────

class MovieSearchView(generics.ListAPIView):
    serializer_class = MovieListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Movie.objects.all()

        q = self.request.query_params.get('q', '').strip()
        genre = self.request.query_params.get('genre', '').strip()
        year = self.request.query_params.get('year')
        language = self.request.query_params.get('language', '').strip()

        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(original_title__icontains=q))
        if genre:
            qs = qs.filter(genre_names__icontains=genre)
        if year:
            qs = qs.filter(release_year=year)
        if language:
            qs = qs.filter(language__icontains=language)

        return qs.order_by('-popularity', '-rating')


# ─── Movie Detail ────────────────────────────────────────────────────────────

class MovieDetailView(generics.RetrieveAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [AllowAny]


# ─── Genres ──────────────────────────────────────────────────────────────────

class GenreListView(generics.ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]


# ─── Home Sections ───────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def trending_week(request):
    movies = list(Movie.objects.order_by('-popularity')[:100])
    selected = random.sample(movies, min(20, len(movies)))
    selected = attach_posters_to_queryset(selected)
    return Response(MovieListSerializer(selected, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def trending_month(request):
    movies = list(Movie.objects.order_by('-popularity')[:200])
    selected = random.sample(movies, min(20, len(movies)))
    selected = attach_posters_to_queryset(selected)
    return Response(MovieListSerializer(selected, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def top_rated_movies(request):
    movies = list(
        Movie.objects.filter(rating__gte=6.5)
        .order_by('-rating')[:100]
    )
    selected = random.sample(movies, min(20, len(movies)))
    selected = attach_posters_to_queryset(selected)
    return Response(MovieListSerializer(selected, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def indian_movies(request):
    movies = list(
        Movie.objects.filter(source='indian')
        .order_by('-popularity')[:100]
    )
    selected = random.sample(movies, min(20, len(movies)))
    selected = attach_posters_to_queryset(selected)
    return Response(MovieListSerializer(selected, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def movies_by_genre(request, genre_name):
    movies = Movie.objects.filter(genre_names__icontains=genre_name)[:50]
    movies = attach_posters_to_queryset(movies)
    return Response(MovieListSerializer(movies, many=True).data)


# ─── Recommendations ─────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommendations_for_user(request):
    movies = get_user_recommendations(request.user, n=20)
    movies = attach_posters_to_queryset(movies)
    return Response(MovieListSerializer(movies, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def similar_movies(request, movie_id):
    try:
        movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        return Response({'error': 'Movie not found'}, status=404)

    movies = get_content_recommendations(movie, n=10)
    movies = attach_posters_to_queryset(movies)
    return Response(MovieListSerializer(movies, many=True).data)


# ─── ✅ IMPORTANT FIX ─────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def all_movies(request):
    """
    GET /api/movies/
    Default endpoint for frontend
    """
    movies = Movie.objects.all().order_by('-popularity')[:20]
    movies = attach_posters_to_queryset(movies)
    return Response(MovieListSerializer(movies, many=True).data)