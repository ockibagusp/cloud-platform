from rest_framework.permissions import BasePermission
from django.contrib.auth.models import AnonymousUser
from supernodes.models import Supernodes
from users.models import User


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
        return is_node.has_permission(request, view) or is_user.has_permission(request, view)


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
        return not isinstance(request.user, Supernodes) and isinstance(request.user, User)


class IsAdmin(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        is_user = IsUser()
        return is_user.has_permission(request, view) and 1 == request.user.is_admin


class IsResearcher(BasePermission):
    """
    Allows access only to researcher users.
    """

    def has_permission(self, request, view):
        is_user = IsUser()
        return is_user.has_permission(request, view) and 0 == request.user.is_admin
