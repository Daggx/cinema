from django.db.models import Count
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser




from cinema.models import Author
from cinema.serializers.author_serializer import AuthorSerializer


class AuthorListAPIView(generics.ListAPIView):
    serializer_class = AuthorSerializer
    def get_queryset(self):
        return (
            Author.objects.select_related("user")
            .annotate(films_count=Count("authors_films"))
        )

class AuthorRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return Author.objects.select_related("user").annotate(
            films_count=Count("authors_films")
        )
    def destroy(self, request, *args, **kwargs):
        author = self.get_object()
        film_count = author.authors_films.count()
        if film_count > 0:
            return Response(
                {"detail": f"Cannot delete the author, he has {film_count} films"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = getattr(author, "user", None)
        if user is not None:
            user.delete()  
            return Response(status=status.HTTP_204_NO_CONTENT)
        super().perform_destroy(author)
        return Response(status=status.HTTP_204_NO_CONTENT)