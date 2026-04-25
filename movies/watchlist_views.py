from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Watchlist
from .serializers import WatchlistSerializer


class WatchlistListView(generics.ListAPIView):
    """GET /api/watchlist/"""
    serializer_class = WatchlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user).select_related('movie').order_by('-added_at')


class WatchlistAddView(generics.CreateAPIView):
    """POST /api/watchlist/add/ — body: {movie_id: <id>}"""
    serializer_class = WatchlistSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        wl = serializer.save()
        return Response(WatchlistSerializer(wl).data, status=status.HTTP_201_CREATED)


class WatchlistRemoveView(generics.DestroyAPIView):
    """DELETE /api/watchlist/<id>/remove/"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)
