from rest_framework import permissions
from rest_framework.exceptions import MethodNotAllowed


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated and request.user.is_admin
        )


class IsAdminOrSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or (
            request.user.is_authenticated and request.user.is_admin
        )


class ProfilePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method not in ("GET", "PATCH"):
            raise MethodNotAllowed(request.method)
        return request.user.is_authenticated


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user) or (
            request.user.is_authenticated and request.user.is_admin
        )


class IsAuthorOrAdminOrModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user.is_admin
            or request.user.is_moderator
            or (obj.author == request.user)
            or request.user.is_staff
        )


class IsAuthorizedOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated
        )
