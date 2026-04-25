# 🎬 CineVerse — Movie Taste Analysis Platform

> Netflix + Letterboxd + AI Assistant + Emotional Intelligence

A full Django + Django REST Framework backend with:
- 10,000+ movies from TMDB + Indian movie datasets
- AI chatbot powered by Groq (LLaMA 3)
- Content-based + user-based recommendation engine
- Emotional intelligence via "What I Watched & Felt"
- OMDb poster enrichment (images only — never for logic)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Redis (for caching) — optional but recommended
- OMDb API key (free at https://www.omdbapi.com/apikey.aspx)
- Groq API key (free at https://console.groq.com)

### Setup

```bash
# Clone / unzip the project
cd cineverse

# Run automated setup
chmod +x setup.sh
./setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # Fill in your API keys!

# Place CSVs in data/
mkdir -p data
cp /path/to/tmdb_5000_movies.csv data/
cp /path/to/tmdb_5000_credits.csv data/
cp /path/to/indian_movies.csv data/

python manage.py makemigrations users movies experience lists ai
python manage.py migrate
python manage.py createsuperuser
python manage.py import_movies    # imports ~10k movies

python manage.py runserver
```

### Import Options
```bash
python manage.py import_movies                  # Full import (both datasets)
python manage.py import_movies --tmdb-only      # Only TMDB
python manage.py import_movies --indian-only    # Only Indian movies
python manage.py import_movies --limit 100      # Test with 100 movies
```

---

## 📡 API Reference

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login → get JWT tokens |
| POST | `/api/auth/logout/` | Logout (blacklist refresh token) |
| GET/PATCH | `/api/auth/profile/` | My profile |
| GET | `/api/auth/user/<username>/` | Public profile |
| POST | `/api/auth/refresh-taste/` | Rebuild taste profile |
| POST | `/api/auth/token/refresh/` | Refresh JWT access token |

### Movies
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/movies/search/?q=inception&genre=thriller` | Search movies |
| GET | `/api/movies/top-rated/` | Top rated (dataset + slight randomization) |
| GET | `/api/movies/trending-week/` | Trending this week |
| GET | `/api/movies/trending-month/` | Trending this month |
| GET | `/api/movies/recommendations/` | Personalised for you 🔐 |
| GET | `/api/movies/genres/` | All genres |
| GET | `/api/movies/genre/<name>/` | Movies by genre |
| GET | `/api/movies/indian/` | Indian movies section |
| GET | `/api/movies/<id>/` | Movie detail |
| GET | `/api/movies/<id>/similar/` | Similar movies |

### Ratings
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/ratings/` | My ratings 🔐 |
| POST | `/api/ratings/rate/` | Rate a movie `{movie_id, rating}` 🔐 |
| DELETE | `/api/ratings/<id>/` | Delete rating 🔐 |

### Watchlist
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/watchlist/` | My watchlist 🔐 |
| POST | `/api/watchlist/add/` | Add to watchlist `{movie_id}` 🔐 |
| DELETE | `/api/watchlist/<id>/remove/` | Remove from watchlist 🔐 |

### Experience ("What I Watched & Felt")
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/experience/` | My experience journal 🔐 |
| POST | `/api/experience/` | Log new experience 🔐 |
| GET | `/api/experience/stats/` | Emotional stats 🔐 |
| GET/PATCH/DELETE | `/api/experience/<id>/` | Experience detail 🔐 |

**Log Experience Body:**
```json
{
  "movie_id": 123,
  "watched": true,
  "rating": 8.5,
  "feeling": "Absolutely loved the emotional depth",
  "mood_tag": "emotional",
  "rewatch": true,
  "review": "One of the best films I've seen this year..."
}
```

### Lists
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/lists/` | Public lists |
| POST | `/api/lists/` | Create list 🔐 |
| GET | `/api/lists/mine/` | My lists 🔐 |
| GET/PATCH/DELETE | `/api/lists/<id>/` | List detail |
| POST | `/api/lists/<id>/add/` | Add movie `{movie_id}` 🔐 |
| POST | `/api/lists/<id>/remove/` | Remove movie 🔐 |
| POST | `/api/lists/<id>/like/` | Toggle like 🔐 |

### AI (CineAI — Groq Powered)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/chat/` | Conversational chatbot |
| GET | `/api/ai/recommend/` | AI personalised recs 🔐 |
| GET | `/api/ai/recommend/?feeling=emotional+inspiring` | Mood-enhanced recs 🔐 |
| GET | `/api/ai/explain/<movie_id>/` | Why recommended for me? 🔐 |
| POST | `/api/ai/compare/` | Compare taste with user 🔐 |
| POST | `/api/ai/list/` | Generate AI curated list 🔐 |
| GET | `/api/ai/ott/<movie_id>/` | OTT platform suggestions |
| POST | `/api/ai/mood/` | Mood-based recs (no login needed) |

**Chat Body:**
```json
{
  "message": "Suggest top 5 emotional Bollywood movies",
  "history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! I'm CineAI..."}
  ]
}
```

**AI List Body:**
```json
{
  "prompt": "Best mind-bending sci-fi movies",
  "save": true,
  "title": "Mind-Benders Collection"
}
```

**Compare Body:**
```json
{"username": "john_doe"}
```

**Mood Body:**
```json
{"feeling": "I want something emotional and uplifting"}
```

---

## 🧠 Architecture

```
cineverse/
├── cineverse/          # Project config (settings, urls, celery)
├── movies/             # Core movie models, search, trending, recs
│   ├── models.py       # Movie, Genre, UserRating, Watchlist
│   ├── omdb_service.py # Poster-only OMDb integration
│   ├── recommendation_engine.py  # TF-IDF content-based + user-based
│   └── management/commands/import_movies.py  # Dataset importer
├── users/              # Custom User model + JWT auth
├── experience/         # "What I Watched & Felt" model
├── lists/              # Movie lists (user + AI generated)
├── ai/                 # Groq-powered AI features
│   ├── groq_service.py # All AI logic (chat, compare, OTT, etc.)
│   └── views.py        # AI API endpoints
└── data/               # Place your CSV datasets here
```

## 🔑 Key Design Decisions

| Rule | Implementation |
|------|---------------|
| **Dataset drives all logic** | trending/top-rated/recs all from DB |
| **OMDb = images only** | `omdb_service.py` only fetches `Poster` field |
| **Posters cached in DB** | `poster_fetched` flag prevents repeat API calls |
| **AI = Groq LLaMA 3** | Fast, free-tier friendly |
| **No repeated OMDb calls** | Once stored, served from DB forever |
| **Taste profile** | Auto-rebuilt after every rating/experience |

## ⚡ Performance

- Trending/top-rated cached in Redis (30min–6hr TTL)
- TF-IDF matrix cached 12 hours
- OMDb results stored in DB permanently
- Django's `select_related` / `prefetch_related` on all list views

## 🌐 Frontend Integration

**Auth header for protected routes:**
```
Authorization: Bearer <access_token>
```

**Refresh token when expired:**
```
POST /api/auth/token/refresh/
{"refresh": "<refresh_token>"}
```
