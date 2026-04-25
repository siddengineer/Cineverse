from django.db import models
from django.conf import settings


class MovieList(models.Model):
    """User-created or AI-generated movie lists."""
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='movie_lists'
    )
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    movies = models.ManyToManyField('movies.Movie', blank=True, related_name='in_lists')
    is_public = models.BooleanField(default=True)
    is_ai_generated = models.BooleanField(default=False)
    ai_prompt = models.TextField(blank=True)        # original AI prompt if generated
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='liked_lists'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.owner}] {self.title}"

    @property
    def like_count(self):
        return self.liked_by.count()

    @property
    def movie_count(self):
        return self.movies.count()
