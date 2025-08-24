from rest_framework import serializers
from cinema.models import FilmRating, AuthorRating
    
class RatingSerializer(serializers.Serializer):
    note = serializers.IntegerField(min_value=1, max_value=5, help_text ="Note from 1 to 5")
    
class FilmRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilmRating
        fields = ["id", "spectator", "film", "note"]
        read_only_fields = ["id", "spectator", "film"]
        
class AuthorRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorRating
        fields = ["id", "spectateur", "auteur", "note"]
        read_only_fields = ["id", "spectateur", "auteur"]