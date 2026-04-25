from django.urls import path
from .watchlist_views import WatchlistListView, WatchlistAddView, WatchlistRemoveView

urlpatterns = [
    path('', WatchlistListView.as_view(), name='watchlist'),
    path('add/', WatchlistAddView.as_view(), name='watchlist-add'),
    path('<int:pk>/remove/', WatchlistRemoveView.as_view(), name='watchlist-remove'),
]
