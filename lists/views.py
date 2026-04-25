from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import MovieList
from .serializers import MovieListSerializer, MovieListSummarySerializer
from movies.models import Movie
from movies.serializers import MovieListSerializer as MovieSerializer


class ListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/lists/        — public lists (+ own private)
    POST /api/lists/        — create a new list
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MovieListSummarySerializer
        return MovieListSerializer

    def get_queryset(self):
        qs = MovieList.objects.all()
        if self.request.user.is_authenticated:
            qs = qs.filter(Q(is_public=True) | Q(owner=self.request.user))
        else:
            qs = qs.filter(is_public=True)
        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ListDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET / PATCH / DELETE /api/lists/<id>/"""
    serializer_class = MovieListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return MovieList.objects.filter(
                Q(is_public=True) | Q(owner=self.request.user)
            )
        return MovieList.objects.filter(is_public=True)

    def update(self, request, *args, **kwargs):
        lst = self.get_object()
        if lst.owner != request.user:
            return Response({'error': 'Not your list.'}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        lst = self.get_object()
        if lst.owner != request.user:
            return Response({'error': 'Not your list.'}, status=403)
        return super().destroy(request, *args, **kwargs)


class MyListsView(generics.ListAPIView):
    """GET /api/lists/mine/ — logged-in user's own lists"""
    serializer_class = MovieListSummarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MovieList.objects.filter(owner=self.request.user).order_by('-created_at')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_movie_to_list(request, list_id):
    """POST /api/lists/<list_id>/add/ — body: {movie_id: <id>}"""
    lst = get_object_or_404(MovieList, id=list_id, owner=request.user)
    movie_id = request.data.get('movie_id')
    if not movie_id:
        return Response({'error': 'movie_id required.'}, status=400)
    movie = get_object_or_404(Movie, id=movie_id)
    lst.movies.add(movie)
    return Response({'message': f'Added "{movie.title}" to "{lst.title}".'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_movie_from_list(request, list_id):
    """POST /api/lists/<list_id>/remove/ — body: {movie_id: <id>}"""
    lst = get_object_or_404(MovieList, id=list_id, owner=request.user)
    movie_id = request.data.get('movie_id')
    movie = get_object_or_404(Movie, id=movie_id)
    lst.movies.remove(movie)
    return Response({'message': f'Removed "{movie.title}" from "{lst.title}".'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like_list(request, list_id):
    """POST /api/lists/<list_id>/like/ — toggle like"""
    lst = get_object_or_404(MovieList, id=list_id, is_public=True)
    user = request.user
    if lst.liked_by.filter(id=user.id).exists():
        lst.liked_by.remove(user)
        liked = False
    else:
        lst.liked_by.add(user)
        liked = True
    return Response({'liked': liked, 'like_count': lst.like_count})
