# tests/test_serializers.py
import datetime as dt
import pytest
from rest_framework.exceptions import ValidationError

from cinema.models import (
    Roles,
    Gender,
    User,
    Spectator,
    Author,
    Film,
    FilmRating,
)
from cinema.serializers.rating_serializer import (
    RatingSerializer,
    FilmRatingSerializer,
)
from cinema.serializers.film_serializer import FilmSerializer, FilmDetailSerializer
from cinema.serializers.author_serializer import AuthorSerializer
from cinema.serializers.auth_serializer import SpectatorRegistrationSerializer, CustomTokenSerializer

pytestmark = pytest.mark.django_db


# ---------- Fixtures ----------
@pytest.fixture
def user():
    return User.objects.create_user(
        email="user@example.com",
        username="user",
        first_name="blablalbalabl",
        last_name="balbllaba",
        password="12345",
        role=Roles.SPECTATOR,
    )


@pytest.fixture
def spectator(user):
    return Spectator.objects.create(user=user, bio="blabla")


@pytest.fixture
def author():
    author_user = User.objects.create_user(
        email="author@example.com",
        username="author",
        first_name="author",
        last_name="author",
        password="author",
        role=Roles.Author,
    )
    return Author.objects.create(
        user=author_user,
        popularity=1.2,
        tmdb_id=12345,
        website="http://author.com",
        gender=Gender.MALE,
        department="Directing",
    )


@pytest.fixture
def film(author):
    film_fix = Film.objects.create(
        title="My Film",
        description="desc",
        release_date=dt.date(2020, 1, 1),
        statut="RELEASED",
        tmdb_id=111,
        budget=1000,
        revenue=2000,
    )
    film_fix.authors.add(author)
    return film_fix


# ---------- RatingSerializer ----------
def test_rating_serializer_valid():
    s = RatingSerializer(data={"note": 5})
    assert s.is_valid(), s.errors
    assert s.validated_data["note"] == 5


def test_rating_serializer_invalid():
    s = RatingSerializer(data={"note": 6})
    assert not s.is_valid()
    assert "note" in s.errors


# ---------- FilmRatingSerializer ----------
def test_film_rating_serializer(spectator, film):
    fr = FilmRating.objects.create(spectator=spectator, film=film, note=4)
    data = FilmRatingSerializer(instance=fr).data
    assert data["note"] == 4
    assert "id" in data



# ---------- FilmSerializer ----------
def test_film_serializer_fields(film):
    data = FilmSerializer(instance=film).data
    assert data["title"] == "My Film"
    assert "budget" in data


def test_film_detail_serializer_includes_authors(film):
    data = FilmDetailSerializer(instance=film).data
    assert len(data["authors"]) == film.authors.count()


# ---------- AuthorSerializer ----------
def test_author_serializer_update_user(author):
    ser = AuthorSerializer(
        instance=author,
        data={
            "user": {
                "first_name": "New",
            },
            "department": "Writing",
        },
        partial=True,
    )
    assert ser.is_valid(), ser.errors
    obj = ser.save()
    obj.user.refresh_from_db()
    assert obj.user.first_name == "New"
    assert obj.department == "Writing"


# ---------- SpectatorRegistrationSerializer ----------
def test_spectator_registration_creates_user_and_profile():
    payload = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "JANE@EXAMPLE.COM",
        "password": "abc12345",
        "bio": "Hi there",
        "date_of_birth": "1990-01-01",
    }
    ser = SpectatorRegistrationSerializer(data=payload)
    assert ser.is_valid(), ser.errors
    user = ser.save()
    assert user.email == "jane@example.com"
    assert user.spectator.bio == "Hi there"


def test_spectator_registration_duplicate_email(user):
    payload = {
        "first_name": "A",
        "last_name": "B",
        "email": "user@example.com",
        "password": "abc12345",
    }
    ser = SpectatorRegistrationSerializer(data=payload)
    assert not ser.is_valid()
    assert "email" in ser.errors


# ---------- CustomTokenSerializer ----------
def test_custom_token_serializer_allows_spectator_login(user):
    ser = CustomTokenSerializer(data={"email": "user@example.com", "password": "12345"})
    assert ser.is_valid(), ser.errors
    data = ser.validated_data
    assert data["user"]["role"] == Roles.SPECTATOR

