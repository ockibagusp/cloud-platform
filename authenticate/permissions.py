from rest_framework.compat import is_authenticated
from rest_framework.permissions import BasePermission
from django.contrib.auth.models import AnonymousUser


class AllowAny(BasePermission):
    """
    Allow any access.
    This isn't strictly required, since you could use an empty
    permission_classes list, but it's useful because it makes the intention
    more explicit.
    """

    def has_permission(self, request, view):
        return True


class IsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users and nodes.
    """

    def has_permission(self, request, view):
        is_node = IsNode()
        is_user = IsUser()
        return is_user.has_permission(request, view) and is_node.has_permission(request, view)


class IsNode(BasePermission):
    """
    Allows access only to authenticated nodes.
    """

    def has_permission(self, request, view):
        return not isinstance(request.user, AnonymousUser)


class IsUser(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        return not isinstance(request.user, AnonymousUser) and is_authenticated(request.user)