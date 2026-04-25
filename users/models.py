from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended user model with movie taste profile."""
    bio = models.TextField(blank=True)
    avatar = models.URLField(blank=True)
    favorite_genres = models.CharField(max_length=500, blank=True)  # comma-separated

    # Taste profile (updated as user interacts)
    taste_profile = models.JSONField(default=dict, blank=True)
    # {
    #   "top_genres": ["Drama", "Thriller"],
    #   "avg_rating": 7.5,
    #   "mood_tags": ["emotional", "mind-blowing"],
    #   "preferred_language": "hi"
    # }

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users_user'

    def __str__(self):
        return self.username

    def update_taste_profile(self):
        """Rebuild taste profile from user's ratings and experiences."""
        from movies.models import UserRating
        from experience.models import UserMovieExperience
        from collections import Counter

        genre_counter = Counter()
        mood_counter = Counter()
        ratings = []

        for r in UserRating.objects.filter(user=self, rating__gte=6).select_related('movie'):
            ratings.append(r.rating)
            for g in (r.movie.genre_names or '').split(','):
                g = g.strip()
                if g:
                    genre_counter[g] += int(r.rating)

        for exp in UserMovieExperience.objects.filter(user=self).select_related('movie'):
            if exp.mood_tag:
                mood_counter[exp.mood_tag] += 1
            if exp.rating and exp.rating >= 6:
                for g in (exp.movie.genre_names or '').split(','):
                    g = g.strip()
                    if g:
                        genre_counter[g] += int(exp.rating)

        self.taste_profile = {
            'top_genres': [g for g, _ in genre_counter.most_common(10)],
            'avg_rating': round(sum(ratings) / len(ratings), 2) if ratings else None,
            'mood_tags': [m for m, _ in mood_counter.most_common(10)],
            'total_rated': len(ratings),
        }
        self.save(update_fields=['taste_profile'])
