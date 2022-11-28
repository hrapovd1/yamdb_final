from rest_framework import permissions


class IsModeratorOrOwnerOrReadOnly(permissions.BasePermission):
    """
    Полное разрешение для Модератора и Владельца,
    только чтение для остальных.
    """
    def has_object_permission(self, request, view, obj):
        if (request.method in permissions.SAFE_METHODS
                or obj.author == request.user):
            return True
        return request.user.is_moderator or request.user.is_admin


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Полное разрешение для Администратора,
    только чтение для остальных.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(request.user, 'role'):  # Отсекаем анонимных пользователей
            return request.user.is_admin
        return False


class IsAdmin(permissions.BasePermission):
    """
    Полное разрешение только для Администратора.
    """
    def has_permission(self, request, view):
        if hasattr(request.user, 'role'):  # Отсекаем анонимных пользователей
            return (
                request.user.is_admin or request.user.is_superuser
            )
        return False
