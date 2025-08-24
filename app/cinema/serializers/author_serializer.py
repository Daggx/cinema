from rest_framework import serializers
from cinema.models import Author, User

from rest_framework import serializers
from django.contrib.auth import get_user_model
from cinema.models import Author

User = get_user_model()


class AuthorUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "username")
        read_only_fields = ("id",)


class AuthorSerializer(serializers.ModelSerializer):
    user = AuthorUserSerializer()

    class Meta:
        model = Author
        fields = (
            "user",
            "popularity",
            "tmdb_id",
            "website",
            "death_date",
            "gender",
            "department",
        )

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()
        return super().update(instance, validated_data)