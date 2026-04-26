"""
Permissions personnalisées
"""
from rest_framework.permissions import BasePermission

class IsOwnerOrReadOnly(BasePermission):
    """Permission - propriétaire ou lecture seule"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return obj.user == request.user
