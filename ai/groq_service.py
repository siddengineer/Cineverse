"""
Groq API service for CineVerse AI features.
All AI intelligence lives here — chatbot, recommendations, taste comparison, OTT detection.
"""
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


# ───────────────── CLIENT ─────────────────

def _get_groq_client():
    try:
        from groq import Groq
        return Groq(api_key=settings.GROQ_API_KEY)
    except ImportError:
        logger.error("groq package not installed. Run: pip install groq")
        return None
    except Exception as e:
        logger.error(f"Groq client init failed: {e}")
        return None


# ───────────────── CORE CHAT ─────────────────

def _chat(messages: list, system: str = '', max_tokens: int = 1024) -> str:
    client = _get_groq_client()
    if not client:
        return "AI service is temporarily unavailable."

    full_messages = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",  # ✅ FIXED MODEL
            messages=full_messages,
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Groq API call failed: {e}")
        return f"AI service error: {str(e)}"


# ───────────────── CHATBOT ─────────────────

CHATBOT_SYSTEM = """You are CineAI, the intelligent movie assistant for CineVerse.

You help users with:
- Movie suggestions by mood, genre, theme
- Movies like X
- Indian/Bollywood/Hollywood movies
- Explain recommendations

Be concise, smart and helpful.
"""


def chatbot_reply(user_message: str, history: list = None, user_context: dict = None) -> str:
    messages = list(history or [])

    system = CHATBOT_SYSTEM
    if user_context:
        genres = user_context.get('top_genres', [])
        moods = user_context.get('mood_tags', [])

        if genres or moods:
            system += "\nUser preferences:\n"
            if genres:
                system += f"Genres: {', '.join(genres[:5])}\n"
            if moods:
                system += f"Moods: {', '.join(moods[:5])}\n"

    messages.append({"role": "user", "content": user_message})

    return _chat(messages, system=system, max_tokens=500)


# ───────────────── EXPLAIN RECOMMENDATION ─────────────────

def explain_recommendation(movie_title: str, user_context: dict, reason_context: str = '') -> str:
    prompt = f"""
Why is "{movie_title}" recommended?
Context: {reason_context}
Keep it short and natural.
"""
    return _chat([{"role": "user", "content": prompt}], max_tokens=150)


# ───────────────── AI LIST GENERATOR ─────────────────

def generate_ai_list_titles(prompt_text: str, available_movies: list) -> list:
    sample = available_movies[:200]

    catalogue = "\n".join(
        f"{m['id']}|{m['title']}|{m.get('genre_names','')}|{m.get('rating','')}"
        for m in sample
    )

    system = """Select best 10 movies. Return only JSON array of IDs."""

    user_msg = f"""
Request: {prompt_text}

Movies:
{catalogue}
"""

    response = _chat([{"role": "user", "content": user_msg}], system=system)

    try:
        import re
        match = re.search(r'\[[\d,\s]+\]', response)
        if match:
            return json.loads(match.group())
    except Exception:
        pass

    return []


# ───────────────── MOOD PARSER ─────────────────

def get_mood_query(feelings_text: str) -> dict:
    system = """Extract genres, moods, keywords from text. Return JSON."""

    response = _chat(
        [{"role": "user", "content": feelings_text}],
        system=system,
        max_tokens=150
    )

    try:
        import re
        match = re.search(r'\{.*\}', response)
        if match:
            return json.loads(match.group())
    except Exception:
        pass

    return {"genres": [], "moods": [], "keywords": []}


# ───────────────── OTT DETECTION ─────────────────

def detect_ott_platforms(movie_title: str, release_year=None, language=''):
    msg = f"{movie_title} ({release_year}) {language}"

    response = _chat([{"role": "user", "content": msg}], max_tokens=150)

    return {
        "platforms": [],
        "confidence": "low",
        "note": response
    }