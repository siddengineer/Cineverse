from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import UserMovieExperience
from .serializers import ExperienceSerializer


class ExperienceListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/experience/         — user's full experience journal
    POST /api/experience/         — log new experience
    """
    serializer_class = ExperienceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserMovieExperience.objects.filter(
            user=self.request.user
        ).select_related('movie')

    def perform_create(self, serializer):
        serializer.save()


class ExperienceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/experience/<id>/"""
    serializer_class = ExperienceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserMovieExperience.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def experience_stats(request):
    """GET /api/experience/stats/ — summary of user's emotional history"""
    from collections import Counter
    from movies.models import UserRating

    experiences = UserMovieExperience.objects.filter(user=request.user)

    mood_counts = Counter(e.mood_tag for e in experiences if e.mood_tag)
    rated = [e.rating for e in experiences if e.rating]
    avg_rating = round(sum(rated) / len(rated), 2) if rated else None

    top_genres = Counter()
    for e in experiences.select_related('movie'):
        for g in (e.movie.genre_names or '').split(','):
            g = g.strip()
            if g:
                top_genres[g] += 1

    return Response({
        'total_watched': experiences.filter(watched=True).count(),
        'total_logged': experiences.count(),
        'avg_personal_rating': avg_rating,
        'mood_breakdown': dict(mood_counts.most_common()),
        'top_genres': dict(top_genres.most_common(10)),
        'rewatched_count': experiences.filter(rewatch=True).count(),
    })
