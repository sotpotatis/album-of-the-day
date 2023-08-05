"""permissions.py
Handles permissions for creating/modifying entries."""
from rest_framework import permissions


class IsAllowedToEdit(permissions.BasePermission):
    """Checks if a user is a staff member, meaning they are allowed to edit entires,
    or if they are not and therefore only have viewing priviliges."""

    def has_permission(self, request, view):
        return request.user.is_staff
