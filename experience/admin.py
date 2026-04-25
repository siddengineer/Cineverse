from django.contrib import admin
from .models import UserMovieExperience


@admin.register(UserMovieExperience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'rating', 'mood_tag', 'watched', 'rewatch', 'created_at']
    list_filter = ['mood_tag', 'watched', 'rewatch']
    search_fields = ['user__username', 'movie__title', 'feeling']
