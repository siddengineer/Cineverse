from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_movies, name='all-movies'),  

    path('search/', views.MovieSearchView.as_view(), name='movie-search'),
    path('top-rated/', views.top_rated_movies, name='top-rated'),
    path('trending-week/', views.trending_week, name='trending-week'),
    path('trending-month/', views.trending_month, name='trending-month'),
    path('recommendations/', views.recommendations_for_user, name='recommendations'),
    path('genres/', views.GenreListView.as_view(), name='genre-list'),
    path('genre/<str:genre_name>/', views.movies_by_genre, name='movies-by-genre'),
    path('indian/', views.indian_movies, name='indian-movies'),
    path('<int:pk>/', views.MovieDetailView.as_view(), name='movie-detail'),
    path('<int:movie_id>/similar/', views.similar_movies, name='similar-movies'),
]