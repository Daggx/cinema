
from rest_framework import serializers
from cinema.models import Film
from cinema.serializers.author_serializer import AuthorSerializer

class FilmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = [
            'id', 'title', 'description', 'release_date', 
            'statut', 'tmdb_id', 'budget', 'revenue'
        ]


class FilmDetailSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    
    class Meta:
        model= Film
        fields = [
            'id', 'title', 'description', 'release_date', 
            'statut', 'tmdb_id', 'budget', 'revenue', "authors"
        ]
        read_only_fields = ('id',)

