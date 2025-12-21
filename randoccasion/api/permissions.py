__all__ = ()

from rest_framework import permissions
from rest_framework_api_key.permissions import HasAPIKey


class AllowCreateWithToken(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return HasAPIKey().has_permission(request, view) or (
                request.user and request.user.is_authenticated
            )

        return request.user and request.user.is_authenticated
