from rest_framework import serializers
from .models import MovieList
# from movies.serializers import MovieListSerializer
from movies.serializers import MovieListSerializer as MovieCardSerializer
from movies.models import Movie


class MovieListSerializer(serializers.ModelSerializer):
    movies = MovieCardSerializer(many=True, read_only=True)
    movie_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Movie.objects.all(), source='movies', write_only=True, required=False
    )
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    movie_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = MovieList
        fields = [
            'id', 'title', 'description', 'owner_username',
            'movies', 'movie_ids', 'is_public', 'is_ai_generated',
            'ai_prompt', 'like_count', 'movie_count', 'is_liked',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'owner_username', 'is_ai_generated', 'ai_prompt', 'created_at', 'updated_at']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.liked_by.filter(id=request.user.id).exists()
        return False


class MovieListSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views (no nested movies)."""
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    movie_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = MovieList
        fields = [
            'id', 'title', 'description', 'owner_username',
            'is_public', 'is_ai_generated', 'like_count', 'movie_count',
            'is_liked', 'created_at',
        ]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.liked_by.filter(id=request.user.id).exists()
        return False
