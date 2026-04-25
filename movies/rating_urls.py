from django.urls import path
from .rating_views import RatingView, RatingListView, DeleteRatingView

urlpatterns = [
    path('', RatingListView.as_view(), name='rating-list'),
    path('rate/', RatingView.as_view(), name='rate-movie'),
    path('<int:pk>/', DeleteRatingView.as_view(), name='delete-rating'),
]
