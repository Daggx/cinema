from rest_framework_simplejwt.views import TokenViewBase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from cinema.models import Roles
from cinema.permissions import IsSpectator


from cinema.serializers.auth_serializer import SpectatorRegistrationSerializer, CustomTokenSerializer

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):

    serializer = SpectatorRegistrationSerializer(data=request.data, context={"request": request})
    if not serializer.is_valid():
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()
    return Response(
        {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
        },
        status=status.HTTP_201_CREATED,
    )




class TokenObtainPairView(TokenViewBase):
    """
    Return JWT tokens (access and refresh) for specific user based on username and password.
    """

    serializer_class = CustomTokenSerializer
    

@api_view(["POST"])
@permission_classes([IsSpectator])
def logout(request):
    """
    Blacklist refresh token => logout
    """
    try:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)

    except Exception:
        return Response(
            {"detail": "Invalid token or already blacklisted."},
            status=status.HTTP_400_BAD_REQUEST,
        )