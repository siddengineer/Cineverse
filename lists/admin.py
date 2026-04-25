from django.contrib import admin
from .models import MovieList


@admin.register(MovieList)
class MovieListAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'is_public', 'is_ai_generated', 'movie_count', 'like_count', 'created_at']
    list_filter = ['is_public', 'is_ai_generated']
    search_fields = ['title', 'owner__username']
    filter_horizontal = ['movies', 'liked_by']
