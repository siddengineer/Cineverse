from django.db import models
from django.conf import settings


class UserMovieExperience(models.Model):
    """
    "What I Watched & Felt" — core emotional intelligence model.
    Drives AI personalization beyond simple ratings.
    """
    MOOD_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('excited', 'Excited'),
        ('scared', 'Scared'),
        ('emotional', 'Emotional'),
        ('mind-blowing', 'Mind-Blowing'),
        ('bored', 'Bored'),
        ('inspired', 'Inspired'),
        ('romantic', 'Romantic'),
        ('tense', 'Tense'),
        ('nostalgic', 'Nostalgic'),
        ('confused', 'Confused'),
        ('amused', 'Amused'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='experiences'
    )
    movie = models.ForeignKey(
        'movies.Movie',
        on_delete=models.CASCADE,
        related_name='experiences'
    )
    watched = models.BooleanField(default=True)
    rating = models.FloatField(null=True, blank=True)       # 1–10, optional
    feeling = models.TextField(blank=True)                  # free text: "loved it", "boring"
    mood_tag = models.CharField(max_length=50, choices=MOOD_CHOICES, blank=True)
    rewatch = models.BooleanField(default=False)            # would rewatch?
    review = models.TextField(blank=True)                   # longer review if wanted
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'movie')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} → {self.movie} [{self.mood_tag}]"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Trigger taste profile update asynchronously
        try:
            self.user.update_taste_profile()
        except Exception:
            pass
