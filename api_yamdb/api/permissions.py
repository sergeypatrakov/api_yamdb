from rest_framework import permissions

from users.models import USER_ROLES


class AdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and request.user.role == USER_ROLES[2][0]
        )
