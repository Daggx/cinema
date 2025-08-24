
import logging
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from cinema.models import Spectator, User, Roles


class SpectatorRegistrationSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "password",
            "bio",
            "date_of_birth",
        )
        extra_kwargs = {
            "email": {"required": True, "allow_blank": False, "allow_null": False},
            "first_name": {"required": True, "allow_blank": False, "allow_null": False},
            "last_name": {"required": True, "allow_blank": False, "allow_null": False},
            "password": {"write_only": True},
        }
        
    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already exists.")
        return email
    
    def validate(self, attrs):
        attrs["email"] = attrs["email"].strip().lower()
        return attrs
    
    def create(self, validated_data):
        bio = validated_data.pop("bio", "") 
        validated_data["username"] = validated_data.get("email")
        
        user = User.objects.create_user(
            role=Roles.SPECTATOR,
            **validated_data
        )
                
        spectator = Spectator(user=user, bio=bio)
        spectator.save()
        return user


class CustomTokenSerializer(TokenObtainPairSerializer):
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token

    def validate(self, attrs):
        attrs["email"] = attrs["email"].lower()
        data = super().validate(attrs)

        if self.user.role != Roles.SPECTATOR:
            raise serializers.ValidationError({"detail": "Only spectators can login for now"})

        data["user"] = {
            "id": self.user.id,
            "username": self.user.email, 
            "email": self.user.email,
            "role": self.user.role,
        }
        return data