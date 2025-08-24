from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


from django.shortcuts import get_object_or_404

from cinema.models import FilmRating, Film, Author, AuthorRating
from cinema.serializers.rating_serializer import RatingSerializer, FilmRatingSerializer, AuthorRatingSerializer
from cinema.serializers.film_serializer import FilmSerializer


# # List favorite movies
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_favorite_films(request):
    films = request.user.spectator.favorite_films.all()
    data = FilmSerializer(films, many=True).data
    return Response(data)


# Add movie into favorites
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_film_to_favorites(request, film_id):
    spectator = request.user.spectator
    film = get_object_or_404(Film, pk=film_id)
    spectator.favorite_films.add(film)
    return Response({"detail": "Film added to favorites."}, status=status.HTTP_200_OK)

    
# # remove a movie from favorites
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_film_from_favorites(request, film_id):
    spectator = request.user.spectator
    film = get_object_or_404(Film, pk=film_id)
    spectator.favorite_films.remove(film)
    return Response({"detail": "Film removed from favorites."}, status=status.HTTP_200_OK)

# # Rate a movie

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def rate_film(request, film_id: int):
    spectator = request.user.spectator
    film = get_object_or_404(Film, pk=film_id)
    serializer = RatingSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    note = serializer.validated_data["note"]
    rating, _ = FilmRating.objects.update_or_create(
        spectator=spectator,
        film=film,
        defaults={"note": note},
    )
    serializer = FilmRatingSerializer(rating)
    return Response(
        {"rating": serializer.data},
        status=status.HTTP_200_OK,
    )


## rATE an author 

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def rate_author(request, author_id: int):
    spectator = request.user.spectator
    author = get_object_or_404(Author, pk=author_id)
    serializer = RatingSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    note = serializer.validated_data["note"]

    rating, _ = AuthorRating.objects.update_or_create(
        spectateur=spectator,
        auteur=author,
        defaults={"note": note},
    )

    serializer = AuthorRatingSerializer(rating)
    return Response({"rating": serializer.data}, status=status.HTTP_200_OK)