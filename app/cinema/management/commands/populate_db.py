from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

from cinema.models import Film, Author, User
from cinema.services.tmdb import TmdbAPI


class Command(BaseCommand):
    help = 'add all popular movies of tmdb (first page) and it directors to the db'

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.TMDB_API_KEY:
            self.stderr.write(self.style.ERROR("api key not found"))
            return

        api = TmdbAPI(api_key=settings.TMDB_API_KEY)

        try:
            self.stdout.write("Getting popular movies data from tmdb")
            popular_movies = api.get_popular_films(page=1)
            results = popular_movies.get("results", [])

            if not results:
                self.stdout.write(self.style.WARNING("No popular movies found on TMDB"))
                return

            for film_data in results:
                tmdb_id = film_data.get("id")
                if not tmdb_id:
                    continue

                self.stdout.write(f"FILm :  '{film_data.get('title')}' (TMDB ID: {tmdb_id})...")

                try:
                    details = api.get_film_details(film_id=str(tmdb_id))
                    credits = api.get_movie_credits(film_id=str(tmdb_id))

                    director_info = next(
                        (member for member in credits.get("crew", []) if member.get("job") == "Director"), 
                        None
                    )
                    if not director_info:
                        self.stdout.write(self.style.WARNING("No director (author)"))
                        continue

                    director_tmdb_id = director_info.get("id")
                    if not director_tmdb_id:
                        continue

                    director_details = api.get_people_detail(person_id=str(director_tmdb_id))
                    user, user_created = User.objects.get_or_create(
                        username=f"author_{director_tmdb_id}",
                        defaults={
                            "first_name": director_details.get('name', '').split(' ')[0],
                            "last_name": director_details.get('name', '').split(' ')[1],
                            "email": f"author_{director_tmdb_id}@example.com",
                            "role": "AUTHOR",
                        },
                    )
                    if user_created:
                        self.stdout.write(self.style.SUCCESS(f"Created User for director {director_details.get('name')}"))

                    author, author_created = Author.objects.update_or_create(
                        tmdb_id=director_tmdb_id,
                        defaults={
                            "user": user,
                            "popularity": director_details.get("popularity", 0.0),
                            "website": director_details.get("homepage"),
                            "death_date": director_details.get("deathday"),
                            "gender": director_details.get("gender", 0),
                            "department": director_details.get("known_for_department"),
                        },
                    )
                    if author_created:
                        self.stdout.write(self.style.SUCCESS(f"Created new author(director ): {author}"))
                    else:
                        self.stdout.write(f"Updated author: {author}")

                    film, film_created = Film.objects.update_or_create(
                        tmdb_id=tmdb_id,
                        defaults={
                            "title": details.get("title"),
                            "description": details.get("overview", ""),
                            "release_date": details.get("release_date"),
                            "budget": details.get("budget"),
                            "revenue": details.get("revenue"),
                        },
                    )
                    if film_created:
                        self.stdout.write(self.style.SUCCESS(f"Added film: {film.title}"))
                    else:
                        self.stdout.write(f"Updated film: {film.title}")

                    film.authors.add(author)
                    self.stdout.write(f"Associated director '{author}' with film '{film.title}'")

                except Exception as movie_error:
                    self.stderr.write(self.style.ERROR(f"Failed to process movie ID {tmdb_id}: {movie_error}"))

            self.stdout.write(self.style.SUCCESS("Finished importing popular movies!"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error fetching popular movies: {e}"))