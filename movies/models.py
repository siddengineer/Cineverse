# from django.db import models
# from django.contrib.auth import get_user_model

# User = get_user_model()


# class Genre(models.Model):
#     name = models.CharField(max_length=100, unique=True)

#     def __str__(self):
#         return self.name

#     class Meta:
#         ordering = ['name']


# class Movie(models.Model):
#     SOURCE_TMDB = 'tmdb'
#     SOURCE_INDIAN = 'indian'
#     SOURCE_CHOICES = [(SOURCE_TMDB, 'TMDB'), (SOURCE_INDIAN, 'Indian')]

#     # Core fields
#     title = models.CharField(max_length=500, db_index=True)
#     original_title = models.CharField(max_length=500, blank=True)
#     overview = models.TextField(blank=True)
#     genres = models.ManyToManyField(Genre, blank=True, related_name='movies')
#     genre_names = models.CharField(max_length=500, blank=True)  # denormalized for fast access

#     # IDs
#     tmdb_id = models.IntegerField(null=True, blank=True, db_index=True)
#     imdb_id = models.CharField(max_length=20, blank=True, db_index=True)

#     # Metadata
#     release_year = models.IntegerField(null=True, blank=True, db_index=True)
#     release_date = models.DateField(null=True, blank=True)
#     runtime = models.IntegerField(null=True, blank=True)  # minutes
#     language = models.CharField(max_length=10, blank=True)
#     source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default=SOURCE_TMDB)

#     # Ratings / popularity (from dataset)
#     rating = models.FloatField(null=True, blank=True, db_index=True)       # TMDB vote_average or IMDB
#     vote_count = models.IntegerField(default=0)
#     popularity = models.FloatField(default=0.0, db_index=True)

#     # Poster (filled via OMDb)
#     poster_url = models.URLField(max_length=1000, blank=True)
#     poster_fetched = models.BooleanField(default=False)

#     # ML feature vector (stored as JSON for recommendations)
#     feature_vector = models.JSONField(null=True, blank=True)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ['-popularity', '-rating']
#         indexes = [
#             models.Index(fields=['rating', 'vote_count']),
#             models.Index(fields=['popularity']),
#             models.Index(fields=['release_year']),
#             models.Index(fields=['source']),
#         ]

#     def __str__(self):
#         return f"{self.title} ({self.release_year})"

#     @property
#     def weighted_rating(self):
#         """IMDB-style weighted rating: (v/(v+m)) * R + (m/(v+m)) * C"""
#         C = 6.0   # mean rating across dataset
#         m = 100   # minimum votes required
#         v = self.vote_count or 0
#         R = self.rating or 0
#         return (v / (v + m)) * R + (m / (v + m)) * C


# class UserRating(models.Model):
#     user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='ratings')
#     movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='user_ratings')
#     rating = models.FloatField()  # 1-10
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         unique_together = ('user', 'movie')

#     def __str__(self):
#         return f"{self.user} rated {self.movie} → {self.rating}"


# class Watchlist(models.Model):
#     user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='watchlist')
#     movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='watchlisted_by')
#     added_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('user', 'movie')

#     def __str__(self):
#         return f"{self.user} → {self.movie}"








from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Movie(models.Model):
    SOURCE_TMDB = 'tmdb'
    SOURCE_INDIAN = 'indian'
    SOURCE_CHOICES = [
        (SOURCE_TMDB, 'TMDB'),
        (SOURCE_INDIAN, 'Indian')
    ]

    # Core fields
    title = models.CharField(max_length=500, db_index=True)
    original_title = models.CharField(max_length=500, blank=True)
    overview = models.TextField(blank=True)
    genres = models.ManyToManyField(Genre, blank=True, related_name='movies')
    genre_names = models.CharField(max_length=500, blank=True)

    # IDs
    tmdb_id = models.IntegerField(null=True, blank=True, db_index=True)
    imdb_id = models.CharField(max_length=20, blank=True, db_index=True)

    # Metadata
    release_year = models.IntegerField(null=True, blank=True, db_index=True)
    release_date = models.DateField(null=True, blank=True)
    runtime = models.IntegerField(null=True, blank=True)
    language = models.CharField(max_length=20, blank=True)

    # 🔥 IMPORTANT FIX
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default=SOURCE_TMDB,
        db_index=True
    )

    # Ratings / popularity
    rating = models.FloatField(null=True, blank=True, db_index=True)
    vote_count = models.IntegerField(default=0)
    popularity = models.FloatField(default=0.0, db_index=True)

    # Poster
    poster_url = models.URLField(max_length=1000, blank=True)
    poster_fetched = models.BooleanField(default=False)

    # ML vector
    feature_vector = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-popularity', '-rating']

        # 🔥 CRITICAL FIX (THIS SOLVES YOUR BUG)
        unique_together = ('title', 'source')

        indexes = [
            models.Index(fields=['rating', 'vote_count']),
            models.Index(fields=['popularity']),
            models.Index(fields=['release_year']),
            models.Index(fields=['source']),
        ]

    def __str__(self):
        return f"{self.title} ({self.release_year})"

    @property
    def weighted_rating(self):
        C = 6.0
        m = 100
        v = self.vote_count or 0
        R = self.rating or 0
        return (v / (v + m)) * R + (m / (v + m)) * C


class UserRating(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='user_ratings')
    rating = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f"{self.user} rated {self.movie} → {self.rating}"


class Watchlist(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='watchlist')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='watchlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f"{self.user} → {self.movie}"