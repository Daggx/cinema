

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from cinema.serializers.film_serializer import FilmSerializer, FilmDetailSerializer
from cinema.models import Film

# List Movies
class FilmAPI(generics.ListAPIView):
    queryset = Film.objects.all()
    serializer_class = FilmSerializer
    
    
class FilterFilmByYearAPI(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = FilmSerializer

    def get_queryset(self):
        year = int(self.kwargs['year'])
        return Film.objects.filter(release_date__year=year).order_by('-created_at')

    

class FilmDetailUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Film.objects.all()
    serializer_class = FilmDetailSerializer

    def get_queryset(self):
        return Film.objects.prefetch_related('authors__user').all()