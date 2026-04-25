from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserRating
from .serializers import UserRatingSerializer


class RatingListView(generics.ListAPIView):
    """GET /api/ratings/ — all ratings by logged-in user"""
    serializer_class = UserRatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserRating.objects.filter(user=self.request.user).select_related('movie')


class RatingView(generics.CreateAPIView):
    """POST /api/ratings/rate/ — rate a movie (creates or updates)"""
    serializer_class = UserRatingSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        rating = serializer.save()
        return Response(UserRatingSerializer(rating, context={'request': request}).data,
                        status=status.HTTP_201_CREATED)


class DeleteRatingView(generics.DestroyAPIView):
    """DELETE /api/ratings/<id>/"""
    serializer_class = UserRatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserRating.objects.filter(user=self.request.user)
