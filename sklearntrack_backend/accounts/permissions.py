# FILE: accounts/permissions.py
# ============================================================================

from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    Checks if user has 'admin' role, is_staff, or is_superuser.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (
                request.user.role == 'admin' or 
                request.user.is_staff or 
                request.user.is_superuser
            )
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admin users to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin users have full access
        if request.user.role == 'admin' or request.user.is_staff or request.user.is_superuser:
            return True
        
        # Check if object has 'user' attribute and matches request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Check if object IS the user
        return obj == request.user


class IsStudentUser(permissions.BasePermission):
    """
    Custom permission to only allow student users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'student'
        )