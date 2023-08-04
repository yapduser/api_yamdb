from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Базовый доступ администратора.

    Доступ разрешен если пользователь аутентифицирован и является
    администратором или суперпользователем.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(IsAdmin):
    """Доступ на изменение для администратора.

    Доступ разрешён на изменение если пользователь аутентифицирован и является
    администратором или суперпользователем.
    """

    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            or request.method in permissions.SAFE_METHODS
        )


class IsAuthorModeratorAdminOrReadOnly(permissions.BasePermission):
    """Доступ автору, модератору, администратору.

    Доступ разрешен если пользователь аутентифицирован и является автором или
    модератором или администратором или суперпользователем.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user == obj.author
            or request.user.is_moderator
            or request.user.is_admin
        )
