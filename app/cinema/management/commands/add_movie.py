from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

from cinema.models import Film, Author, User
from cinema.services.tmdb import TmdbAPI 


class Command(BaseCommand):
    help = 'add a movie and it director to the DB (from imdb id)'

    def add_arguments(self, parser):
        parser.add_argument('tmdb_id', type=int, help='The TMDB id of the movie to be added')

    @transaction.atomic
    def handle(self, *args, **options):
        tmdb_id = options['tmdb_id']
        
        if not settings.TMDB_API_KEY:
            self.stderr.write(self.style.ERROR("tmdb api not found"))
            return

        api = TmdbAPI(api_key=settings.TMDB_API_KEY)

        try:
            self.stdout.write(f"Getting details for movie with TMDB ID: {tmdb_id}...")
            film_data = api.get_film_details(film_id=str(tmdb_id))
            credits_data = api.get_movie_credits(film_id=str(tmdb_id))
            director_info = next((member for member in credits_data.get('crew', []) if member.get('job') == 'Director'), None)

            if not director_info:
                return

            director_tmdb_id = director_info.get('id')
            if not director_tmdb_id:
                return
                
            director_details = api.get_people_detail(person_id=str(director_tmdb_id))
            user, user_created = User.objects.get_or_create(
                username=f"author_{director_tmdb_id}",
                defaults={
                    'first_name': director_details.get('name', '').split(' ')[0],
                    'last_name': director_details.get('name', '').split(' ')[1],
                    'email': f"author_{director_tmdb_id}@example.com", #Random email for the moment because authors is abstractUser that need an email
                    'role': 'AUTHOR',
                }
            )

            if user_created:
                self.stdout.write(self.style.SUCCESS(f"Created new User for author: {user}"))
            author, author_created = Author.objects.update_or_create(
                tmdb_id=director_tmdb_id,
                defaults={
                    'user': user,
                    'popularity': director_details.get('popularity', 0.0),
                    'website': director_details.get('homepage'),
                    'death_date': director_details.get('deathday'), 
                    'gender': director_details.get('gender', 0),
                    'department': director_details.get('known_for_department'),
                }
            )
            
            if author_created:
                self.stdout.write(self.style.SUCCESS(f"Successfully created new author: {author}"))
            else:
                self.stdout.write(f"Successfully updated existing author: {author}")

            film, film_created = Film.objects.update_or_create(
                tmdb_id=tmdb_id,
                defaults={
                    'title': film_data.get('title'),
                    'description': film_data.get('overview', ''),
                    'release_date': film_data.get('release_date'),
                    'budget': film_data.get('budget'),
                    'revenue': film_data.get('revenue'),
                }
            )

            if film_created:
                self.stdout.write(self.style.SUCCESS(f"Successfully added new film: '{film.title}'"))
            else:
                self.stdout.write(f"Successfully updated existing film: '{film.title}'")
            film.authors.add(author)
            self.stdout.write(f"Successfully associated director '{author}' with film '{film.title}'")

            self.stdout.write(self.style.SUCCESS("\nCommand completed successfully!"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))