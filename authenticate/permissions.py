from rest_framework.compat import is_authenticated
from rest_framework.permissions import BasePermission
from django.contrib.auth.models import AnonymousUser


class IsAuthenticated(BasePermission):
    """
    Allows access only to authenticated nodes.
    """

    def has_permission(self, request, view):
        return not isinstance(request.user, AnonymousUser) \
               or (request.user and is_authenticated(request.user))

