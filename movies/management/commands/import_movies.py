# """
# Django management command to import movies from CSV files into the database.
 
# Place this file at:
#     movies/management/commands/import_movies.py
 
# Make sure these dirs exist (create __init__.py in each):
#     movies/management/__init__.py
#     movies/management/commands/__init__.py
 
# Then run:
#     python manage.py import_movies
# """
 
# import csv
# import json
# import os
# import ast
# from django.core.management.base import BaseCommand
# from django.conf import settings
 
 
# class Command(BaseCommand):
#     help = 'Import movies from TMDB and Indian Movies CSV files'
 
#     def add_arguments(self, parser):
#         parser.add_argument(
#             '--clear',
#             action='store_true',
#             help='Clear existing movies before importing',
#         )
 
#     def handle(self, *args, **options):
#         from movies.models import Movie, Genre
 
#         if options.get('clear'):
#             self.stdout.write('Clearing existing movies...')
#             Movie.objects.all().delete()
#             Genre.objects.all().delete()
 
#         tmdb_movies_csv = settings.TMDB_MOVIES_CSV
#         indian_csv = settings.INDIAN_MOVIES_CSV
 
#         # Try alternate filenames for Indian CSV (space vs underscore in filename)
#         if not os.path.exists(indian_csv):
#             data_dir = os.path.dirname(indian_csv)
#             for candidate in ['indian movies.csv', 'Indian Movies.csv', 'Indian_Movies.csv', 'indianmovies.csv']:
#                 alt = os.path.join(data_dir, candidate)
#                 if os.path.exists(alt):
#                     indian_csv = alt
#                     self.stdout.write(f'Found Indian CSV at: {alt}')
#                     break
 
#         # ── Import TMDB movies ────────────────────────────────────────────────
#         if os.path.exists(tmdb_movies_csv):
#             self.stdout.write(f'Importing TMDB movies from {tmdb_movies_csv}...')
#             self._import_tmdb(tmdb_movies_csv, Movie, Genre)
#         else:
#             self.stdout.write(self.style.WARNING(f'TMDB movies CSV not found: {tmdb_movies_csv}'))
 
#         # ── Import Indian movies ──────────────────────────────────────────────
#         if os.path.exists(indian_csv):
#             self.stdout.write(f'Importing Indian movies from {indian_csv}...')
#             self._import_indian(indian_csv, Movie, Genre)
#         else:
#             self.stdout.write(self.style.WARNING(f'Indian movies CSV not found: {indian_csv}'))
 
#         self.stdout.write(self.style.SUCCESS(
#             f'Done! Total movies in DB: {Movie.objects.count()}'
#         ))
 
#     def _parse_genres(self, genres_raw):
#         """Parse genres field — handles both JSON and plain string."""
#         if not genres_raw:
#             return [], ''
#         try:
#             # TMDB format: [{"id": 28, "name": "Action"}, ...]
#             genres = json.loads(genres_raw)
#             names = [g['name'] for g in genres if 'name' in g]
#             return names, ', '.join(names)
#         except (json.JSONDecodeError, TypeError):
#             try:
#                 genres = ast.literal_eval(genres_raw)
#                 if isinstance(genres, list):
#                     names = [g.get('name', g) if isinstance(g, dict) else str(g) for g in genres]
#                     return names, ', '.join(names)
#             except Exception:
#                 pass
#             # Plain comma-separated string
#             names = [g.strip() for g in str(genres_raw).split(',') if g.strip()]
#             return names, ', '.join(names)
 
#     def _safe_float(self, val, default=0.0):
#         try:
#             return float(val) if val not in (None, '', 'nan', 'NaN') else default
#         except (ValueError, TypeError):
#             return default
 
#     def _safe_int(self, val, default=0):
#         try:
#             return int(float(val)) if val not in (None, '', 'nan', 'NaN') else default
#         except (ValueError, TypeError):
#             return default
 
#     def _import_tmdb(self, csv_path, Movie, Genre):
#         created = updated = skipped = 0
 
#         with open(csv_path, encoding='utf-8', errors='replace') as f:
#             reader = csv.DictReader(f)
#             rows = list(reader)
 
#         self.stdout.write(f'  Found {len(rows)} rows in TMDB CSV')
 
#         for row in rows:
#             try:
#                 title = (row.get('title') or row.get('original_title') or '').strip()
#                 if not title:
#                     skipped += 1
#                     continue
 
#                 genre_names_list, genre_names_str = self._parse_genres(row.get('genres', ''))
#                 release_date = row.get('release_date', '') or ''
#                 release_year = None
#                 if release_date and len(release_date) >= 4:
#                     try:
#                         release_year = int(release_date[:4])
#                     except ValueError:
#                         pass
 
#                 tmdb_id = self._safe_int(row.get('id') or row.get('tmdb_id'))
 
#                 defaults = {
#                     'title': title,
#                     'original_title': (row.get('original_title') or title).strip(),
#                     'overview': (row.get('overview') or '').strip(),
#                     'release_year': release_year,
#                     'language': (row.get('original_language') or 'en').strip(),
#                     'genre_names': genre_names_str,
#                     'rating': self._safe_float(row.get('vote_average')),
#                     'vote_count': self._safe_int(row.get('vote_count')),
#                     'popularity': self._safe_float(row.get('popularity')),
#                     'runtime': self._safe_int(row.get('runtime')),
#                     'source': Movie.SOURCE_TMDB if hasattr(Movie, 'SOURCE_TMDB') else 'tmdb',
#                 }
 
#                 if tmdb_id:
#                     movie, was_created = Movie.objects.update_or_create(
#                         tmdb_id=tmdb_id,
#                         defaults=defaults,
#                     )
#                 else:
#                     movie, was_created = Movie.objects.get_or_create(
#                         title=title,
#                         release_year=release_year,
#                         defaults=defaults,
#                     )
 
#                 # Link Genre objects
#                 for gname in genre_names_list:
#                     genre, _ = Genre.objects.get_or_create(name=gname)
#                     movie.genres.add(genre)
 
#                 if was_created:
#                     created += 1
#                 else:
#                     updated += 1
 
#                 if (created + updated) % 500 == 0:
#                     self.stdout.write(f'  ... {created + updated} processed')
 
#             except Exception as e:
#                 skipped += 1
#                 if skipped <= 5:
#                     self.stdout.write(self.style.WARNING(f'  Skipped row: {e}'))
 
#         self.stdout.write(self.style.SUCCESS(
#             f'  TMDB: {created} created, {updated} updated, {skipped} skipped'
#         ))
 
#     def _import_indian(self, csv_path, Movie, Genre):
#         created = updated = skipped = 0
 
#         with open(csv_path, encoding='utf-8', errors='replace') as f:
#             reader = csv.DictReader(f)
#             rows = list(reader)
 
#         self.stdout.write(f'  Found {len(rows)} rows in Indian movies CSV')
 
#         # Detect column names (different CSVs have different headers)
#         if rows:
#             sample = rows[0]
#             keys = list(sample.keys())
#             self.stdout.write(f'  Columns: {keys[:10]}')
 
#         for row in rows:
#             try:
#                 # Try various common column name patterns
#                 title = (
#                     row.get('title') or row.get('Title') or
#                     row.get('name') or row.get('Name') or
#                     row.get('movie_title') or row.get('Movie Title') or ''
#                 ).strip()
 
#                 if not title:
#                     skipped += 1
#                     continue
 
#                 genre_raw = (
#                     row.get('genre') or row.get('Genre') or
#                     row.get('genres') or row.get('Genres') or ''
#                 )
#                 genre_names_list, genre_names_str = self._parse_genres(genre_raw)
 
#                 year_raw = (
#                     row.get('year') or row.get('Year') or
#                     row.get('release_year') or row.get('Release Year') or
#                     row.get('release_date') or row.get('Release Date') or ''
#                 )
#                 release_year = None
#                 if year_raw:
#                     try:
#                         release_year = int(str(year_raw).strip()[:4])
#                     except ValueError:
#                         pass
 
#                 rating_raw = (
#                     row.get('rating') or row.get('Rating') or
#                     row.get('imdb_rating') or row.get('IMDB Rating') or
#                     row.get('score') or '0'
#                 )
#                 rating = self._safe_float(rating_raw)
#                 # Normalize: if rating looks like it's out of 100, scale down
#                 if rating > 10:
#                     rating = rating / 10
 
#                 vote_raw = (
#                     row.get('votes') or row.get('Votes') or
#                     row.get('vote_count') or row.get('num_votes') or '0'
#                 )
 
#                 language_raw = (
#                     row.get('language') or row.get('Language') or
#                     row.get('lang') or 'hi'
#                 )
 
#                 overview = (
#                     row.get('overview') or row.get('Overview') or
#                     row.get('description') or row.get('Description') or
#                     row.get('plot') or row.get('Plot') or ''
#                 ).strip()
 
#                 defaults = {
#                     'title': title,
#                     'original_title': title,
#                     'overview': overview,
#                     'release_year': release_year,
#                     'language': str(language_raw).strip().lower()[:10],
#                     'genre_names': genre_names_str,
#                     'rating': rating,
#                     'vote_count': self._safe_int(vote_raw),
#                     'popularity': self._safe_float(row.get('popularity') or rating * 10),
#                     'source': Movie.SOURCE_INDIAN if hasattr(Movie, 'SOURCE_INDIAN') else 'indian',
#                 }
 
#                 movie, was_created = Movie.objects.get_or_create(
#                     title=title,
#                     release_year=release_year,
#                     defaults=defaults,
#                 )
 
#                 for gname in genre_names_list:
#                     genre, _ = Genre.objects.get_or_create(name=gname)
#                     movie.genres.add(genre)
 
#                 if was_created:
#                     created += 1
#                 else:
#                     updated += 1
 
#                 if (created + updated) % 200 == 0:
#                     self.stdout.write(f'  ... {created + updated} processed')
 
#             except Exception as e:
#                 skipped += 1
#                 if skipped <= 5:
#                     self.stdout.write(self.style.WARNING(f'  Skipped row: {e}'))
 
#         self.stdout.write(self.style.SUCCESS(
#             f'  Indian: {created} created, {updated} updated, {skipped} skipped'
#         ))


import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Import movies from TMDB and Indian Movies CSV files'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true')

    def handle(self, *args, **options):
        from movies.models import Movie, Genre

        if options.get('clear'):
            self.stdout.write("Clearing DB...")
            Movie.objects.all().delete()
            Genre.objects.all().delete()

        tmdb_csv = settings.TMDB_MOVIES_CSV
        indian_csv = settings.INDIAN_MOVIES_CSV

        print("TMDB PATH:", tmdb_csv)
        print("INDIAN PATH:", indian_csv)

        if os.path.exists(tmdb_csv):
            self.stdout.write("Importing TMDB...")
            self._import_tmdb(tmdb_csv, Movie, Genre)

        if os.path.exists(indian_csv):
            self.stdout.write("Importing Indian movies...")
            self._import_indian(indian_csv, Movie, Genre)
        else:
            print("❌ Indian CSV NOT FOUND")

        self.stdout.write(self.style.SUCCESS(
            f"Done! Total movies: {Movie.objects.count()}"
        ))

    # ---------------- HELPERS ----------------

    def _safe_float(self, val):
        try:
            return float(val)
        except:
            return 0.0

    def _safe_int(self, val):
        try:
            return int(float(val))
        except:
            return 0

    def _parse_genres(self, raw):
        if not raw:
            return [], ''
        names = [g.strip() for g in str(raw).split(',') if g.strip()]
        return names, ', '.join(names)

    # ---------------- TMDB ----------------

    def _import_tmdb(self, path, Movie, Genre):
        created = skipped = 0

        with open(path, encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)

            for i, row in enumerate(reader, start=1):
                try:
                    title = row.get('title') or row.get('original_title')
                    if not title:
                        continue

                    genres_list, genres_str = self._parse_genres(row.get('genres'))

                    movie, was_created = Movie.objects.get_or_create(
                        title=title.strip(),
                        source='tmdb',
                        defaults={
                            'original_title': title.strip(),
                            'overview': row.get('overview') or '',
                            'release_year': self._safe_int(row.get('release_date')[:4]) if row.get('release_date') else None,
                            'language': row.get('original_language') or 'en',
                            'genre_names': genres_str,
                            'rating': self._safe_float(row.get('vote_average')),
                            'vote_count': self._safe_int(row.get('vote_count')),
                            'popularity': self._safe_float(row.get('popularity')),
                        }
                    )

                    for g in genres_list:
                        genre, _ = Genre.objects.get_or_create(name=g)
                        movie.genres.add(genre)

                    if was_created:
                        created += 1
                    else:
                        skipped += 1

                    if i % 500 == 0:
                        print(f"TMDB: {i}")

                except Exception as e:
                    print("TMDB ERROR:", e)

        print(f"TMDB DONE: {created} created, {skipped} skipped")

    # ---------------- INDIAN (FIXED) ----------------

    def _import_indian(self, path, Movie, Genre):
        created = skipped = 0

        with open(path, encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)

            for i, row in enumerate(reader, start=1):
                try:
                    title = row.get('Movie Name') or ''
                    if not title:
                        continue

                    title = title.strip()
                    genres_list, genres_str = self._parse_genres(row.get('Genre'))

                    # ✅ FIXED: use get_or_create instead of create to handle duplicates
                    movie, was_created = Movie.objects.get_or_create(
                        title=title,
                        source='indian',
                        defaults={
                            'original_title': title,
                            'overview': '',
                            'release_year': self._safe_int(row.get('Year')),
                            'language': (row.get('Language') or 'hindi').strip().lower(),
                            'genre_names': genres_str,
                            'rating': self._safe_float(row.get('Rating(10)')),
                            'vote_count': self._safe_int(row.get('Votes')),
                            'popularity': 0,
                        }
                    )

                    for g in genres_list:
                        genre, _ = Genre.objects.get_or_create(name=g)
                        movie.genres.add(genre)

                    if was_created:
                        created += 1
                    else:
                        skipped += 1

                    if i % 500 == 0:
                        print(f"INDIAN: {i}")

                except Exception as e:
                    print("INDIAN ERROR:", e)

        print(f"INDIAN DONE: {created} created, {skipped} skipped")