from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class IsAdminOrSubAdminReadBook(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and (
                user.is_superuser or user.has_perm('sub_admins.ReadBook')
            )
        )


class IsAdminOrSubAdminUpdateBook(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and (
                user.is_superuser or user.has_perm('sub_admins.UpdateBook')
            )
        )


class IsAdminOrSubAdminDeleteBook(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and (
                user.is_superuser or user.has_perm('sub_admins.DeleteBook')
            )
        )
