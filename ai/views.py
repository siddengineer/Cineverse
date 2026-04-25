import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

from . import groq_service
from movies.models import Movie
from movies.serializers import MovieListSerializer
from movies.omdb_service import attach_posters_to_queryset
from movies.recommendation_engine import get_content_recommendations
from lists.models import MovieList

logger = logging.getLogger(__name__)
User = get_user_model()


# ─── Chatbot ──────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def chat(request):
    """
    POST /api/ai/chat/
    Body: {message: str, history: [{role, content}]}
    """
    message = request.data.get('message', '').strip()
    if not message:
        return Response({'error': 'message is required.'}, status=400)

    history = request.data.get('history', [])
    # Validate history format
    history = [
        h for h in history
        if isinstance(h, dict) and h.get('role') in ('user', 'assistant') and h.get('content')
    ][-20:]  # max last 20 turns

    user_context = {}
    if request.user.is_authenticated:
        user_context = request.user.taste_profile or {}

    reply = groq_service.chatbot_reply(message, history, user_context)
    return Response({
        'reply': reply,
        'history': history + [
            {'role': 'user', 'content': message},
            {'role': 'assistant', 'content': reply},
        ]
    })


# ─── AI Recommendations ───────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_recommend(request):
    """
    GET /api/ai/recommend/
    AI-enhanced personalised recommendations using taste profile + feelings.
    """
    user = request.user
    taste = user.taste_profile or {}
    top_genres = taste.get('top_genres', [])
    mood_tags = taste.get('mood_tags', [])

    # If user has feelings logged, use AI to extract deeper query
    extra_feelings = request.query_params.get('feeling', '')
    ai_genres, ai_moods, ai_keywords = [], [], []

    if extra_feelings:
        parsed = groq_service.get_mood_query(extra_feelings)
        ai_genres = parsed.get('genres', [])
        ai_moods = parsed.get('moods', [])
        ai_keywords = parsed.get('keywords', [])

    combined_genres = list(set(top_genres + ai_genres))[:8]
    combined_keywords = ai_keywords

    # Build DB query from AI-understood preferences
    from django.db.models import Q
    q = Q()
    for genre in combined_genres[:5]:
        q |= Q(genre_names__icontains=genre)
    for kw in combined_keywords[:3]:
        q |= Q(overview__icontains=kw)

    if q:
        # Exclude already rated / watchlisted
        from movies.models import UserRating, Watchlist
        seen_ids = set(
            list(UserRating.objects.filter(user=user).values_list('movie_id', flat=True)) +
            list(Watchlist.objects.filter(user=user).values_list('movie_id', flat=True))
        )
        candidates = list(
            Movie.objects.filter(q).exclude(id__in=seen_ids).order_by('-rating', '-popularity')[:30]
        )
    else:
        from movies.recommendation_engine import get_user_recommendations
        candidates = get_user_recommendations(user, n=20)

    candidates = attach_posters_to_queryset(candidates[:20])

    # Get AI explanations for top 5
    explanations = {}
    for movie in candidates[:5]:
        try:
            exp = groq_service.explain_recommendation(
                movie.title, taste,
                reason_context=f"Genres: {movie.genre_names}, Rating: {movie.rating}"
            )
            explanations[movie.id] = exp
        except Exception:
            pass

    serializer = MovieListSerializer(candidates, many=True)
    return Response({
        'movies': serializer.data,
        'explanations': explanations,
        'based_on': {
            'genres': combined_genres,
            'moods': list(set(mood_tags + ai_moods)),
            'keywords': combined_keywords,
        }
    })


# ─── Explain Recommendation ───────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_explain(request, movie_id):
    """GET /api/ai/explain/<movie_id>/ — why is this movie recommended for me?"""
    try:
        movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        return Response({'error': 'Movie not found.'}, status=404)

    taste = request.user.taste_profile or {}
    explanation = groq_service.explain_recommendation(
        movie.title, taste,
        reason_context=f"Genres: {movie.genre_names}, Overview: {movie.overview[:200]}"
    )
    return Response({'movie': movie.title, 'explanation': explanation})


# ─── Taste Comparison ─────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def compare_taste(request):
    """
    POST /api/ai/compare/
    Body: {username: "other_user"}
    Compare taste between logged-in user and another user.
    """
    other_username = request.data.get('username', '').strip()
    if not other_username:
        return Response({'error': 'username is required.'}, status=400)

    try:
        other_user = User.objects.get(username=other_username)
    except User.DoesNotExist:
        return Response({'error': f'User "{other_username}" not found.'}, status=404)

    if other_user == request.user:
        return Response({'error': 'Cannot compare with yourself.'}, status=400)

    result = groq_service.compare_taste(
        user1_profile=request.user.taste_profile or {},
        user2_profile=other_user.taste_profile or {},
        user1_name=request.user.username,
        user2_name=other_user.username,
    )
    return Response(result)


# ─── AI List Generator ────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_generate_list(request):
    """
    POST /api/ai/list/
    Body: {prompt: "Best emotional Bollywood movies", save: true, title: "My List"}
    Generates a curated movie list from dataset using AI.
    """
    prompt_text = request.data.get('prompt', '').strip()
    if not prompt_text:
        return Response({'error': 'prompt is required.'}, status=400)

    save_list = request.data.get('save', False)
    list_title = request.data.get('title', prompt_text[:100])

    # Get a sample of movies for AI to choose from
    # Mix: filter by keywords from prompt heuristically first
    words = prompt_text.lower().split()
    from django.db.models import Q
    q = Q()
    for word in words:
        if len(word) > 3:  # skip short words
            q |= Q(genre_names__icontains=word) | Q(title__icontains=word)

    if q:
        sample_qs = Movie.objects.filter(q).order_by('-rating')[:300]
    else:
        sample_qs = Movie.objects.order_by('-popularity')[:300]

    movie_data = list(sample_qs.values('id', 'title', 'genre_names', 'rating', 'release_year', 'overview'))

    # Ask AI to select best matches
    selected_ids = groq_service.generate_ai_list_titles(prompt_text, movie_data)

    if not selected_ids:
        return Response({'error': 'AI could not generate a list. Try a different prompt.'}, status=400)

    movies = list(Movie.objects.filter(id__in=selected_ids))
    # Preserve AI order
    id_index = {mid: i for i, mid in enumerate(selected_ids)}
    movies.sort(key=lambda m: id_index.get(m.id, 999))
    movies = attach_posters_to_queryset(movies)

    serializer = MovieListSerializer(movies, many=True)
    response_data = {
        'prompt': prompt_text,
        'movies': serializer.data,
    }

    # Optionally save as a list
    if save_list:
        lst = MovieList.objects.create(
            owner=request.user,
            title=list_title,
            description=f'AI-generated list for: "{prompt_text}"',
            is_ai_generated=True,
            ai_prompt=prompt_text,
        )
        lst.movies.set(movies)
        response_data['list_id'] = lst.id
        response_data['message'] = f'List "{list_title}" saved successfully.'

    return Response(response_data)


# ─── OTT Platform Detection ───────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def ott_detect(request, movie_id):
    """GET /api/ai/ott/<movie_id>/ — which platforms might have this movie?"""
    try:
        movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        return Response({'error': 'Movie not found.'}, status=404)

    result = groq_service.detect_ott_platforms(
        movie_title=movie.title,
        release_year=movie.release_year,
        language=movie.language,
    )
    return Response({
        'movie': movie.title,
        'release_year': movie.release_year,
        **result,
    })


# ─── Mood-Based Quick Reco ────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def mood_recommend(request):
    """
    POST /api/ai/mood/
    Body: {feeling: "I want something emotional and inspiring"}
    Quick recommendation based on feeling text — no login needed.
    """
    feeling = request.data.get('feeling', '').strip()
    if not feeling:
        return Response({'error': 'feeling is required.'}, status=400)

    parsed = groq_service.get_mood_query(feeling)
    genres = parsed.get('genres', [])
    keywords = parsed.get('keywords', [])

    from django.db.models import Q
    q = Q()
    for genre in genres:
        q |= Q(genre_names__icontains=genre)
    for kw in keywords:
        q |= Q(overview__icontains=kw)

    if not q:
        movies = list(Movie.objects.order_by('-popularity')[:20])
    else:
        movies = list(Movie.objects.filter(q).order_by('-rating', '-popularity')[:20])

    movies = attach_posters_to_queryset(movies)
    serializer = MovieListSerializer(movies, many=True)
    return Response({
        'feeling_parsed': parsed,
        'movies': serializer.data,
    })
