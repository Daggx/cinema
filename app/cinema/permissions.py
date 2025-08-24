
from rest_framework.permissions import BasePermission
from cinema.models import Roles


class IsSpectator(BasePermission):
    """
    Permission to allow only Spectator users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.role == Roles.SPECTATOR
