from django.urls import path

from cinema.views import auth, authors, films, ratings_favorites_spectator
from rest_framework_simplejwt.views import TokenRefreshView


app_name = "cinema"

urlpatterns = [
    #Spectator
    path("register/", auth.register, name="register_spectator"),
    path("login/", auth.TokenObtainPairView.as_view(), name="login_spectator"),
    path("logout/", auth.logout, name="logout_spectator"),
    path("refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("favorites/films/", ratings_favorites_spectator.list_favorite_films, name="my-favorite-films"),
    path("favorites/films/<int:film_id>/add/", ratings_favorites_spectator.add_film_to_favorites, name="add-favorite-film"),
    path("favorites/films/<int:film_id>/remove/", ratings_favorites_spectator.remove_film_from_favorites, name="remove-favorite-film"),
    path("films/<int:film_id>/rate/", ratings_favorites_spectator.rate_film, name="rate-film"),
    path("authors/<int:author_id>/rate/", ratings_favorites_spectator.rate_author, name="rate-author"),
    
    #Authors
    path("authors/", authors.AuthorListAPIView.as_view(), name="list-authors"),
    path("authors/<int:pk>/", authors.AuthorRetrieveUpdateDestroyAPIView.as_view(), name="author-detail"),
    #Film
    path("films/",films.FilmAPI.as_view(), name="list-movies"),
    path('films/<int:year>/', films.FilterFilmByYearAPI.as_view(), name='films-by-year'),
    path("films/<int:pk>/", films.FilmDetailUpdateView.as_view(), name="movie-update-retrieve"),
]
