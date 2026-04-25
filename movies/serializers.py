from rest_framework import serializers
from .models import Movie, Genre, UserRating, Watchlist


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']


class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    user_rating = serializers.SerializerMethodField()
    in_watchlist = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'original_title', 'overview',
            'genres', 'genre_names', 'release_year', 'language',
            'imdb_id', 'tmdb_id', 'rating', 'vote_count', 'popularity',
            'poster_url', 'runtime', 'source',
            'user_rating', 'in_watchlist',
        ]

    def get_user_rating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                rating = UserRating.objects.get(user=request.user, movie=obj)
                return rating.rating
            except UserRating.DoesNotExist:
                pass
        return None

    def get_in_watchlist(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Watchlist.objects.filter(user=request.user, movie=obj).exists()
        return False


class MovieListSerializer(serializers.ModelSerializer):
    """Lighter serializer for lists/trending"""
    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'release_year', 'genre_names',
            'rating', 'popularity', 'poster_url', 'overview', 'language',
        ]


class UserRatingSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(), source='movie', write_only=True
    )

    class Meta:
        model = UserRating
        fields = ['id', 'movie', 'movie_id', 'rating', 'created_at']

    def validate_rating(self, value):
        if not (1 <= value <= 10):
            raise serializers.ValidationError("Rating must be between 1 and 10.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        movie = validated_data['movie']
        rating, _ = UserRating.objects.update_or_create(
            user=user, movie=movie,
            defaults={'rating': validated_data['rating']}
        )
        return rating


class WatchlistSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(), source='movie', write_only=True
    )

    class Meta:
        model = Watchlist
        fields = ['id', 'movie', 'movie_id', 'added_at']

    def create(self, validated_data):
        user = self.context['request'].user
        wl, created = Watchlist.objects.get_or_create(
            user=user, movie=validated_data['movie']
        )
        return wl
