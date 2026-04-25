from django.contrib import admin
from .models import Movie, Genre, UserRating, Watchlist


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'release_year', 'rating', 'popularity', 'source', 'poster_fetched', 'language']
    list_filter = ['source', 'poster_fetched', 'language']
    search_fields = ['title', 'imdb_id', 'tmdb_id']
    filter_horizontal = ['genres']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'rating', 'created_at']
    list_filter = ['rating']


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'added_at']
