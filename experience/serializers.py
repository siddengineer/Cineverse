from rest_framework import serializers
from .models import UserMovieExperience
from movies.serializers import MovieListSerializer
from movies.models import Movie


class ExperienceSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(), source='movie', write_only=True
    )

    class Meta:
        model = UserMovieExperience
        fields = [
            'id', 'movie', 'movie_id',
            'watched', 'rating', 'feeling', 'mood_tag',
            'rewatch', 'review', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_rating(self, value):
        if value is not None and not (1 <= value <= 10):
            raise serializers.ValidationError("Rating must be 1–10.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        movie = validated_data['movie']
        exp, _ = UserMovieExperience.objects.update_or_create(
            user=user, movie=movie,
            defaults={k: v for k, v in validated_data.items() if k != 'movie'}
        )
        return exp
