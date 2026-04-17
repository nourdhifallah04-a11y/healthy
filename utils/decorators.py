"""
Custom decorators for the application.
"""

from functools import wraps
from django.http import JsonResponse


def json_response(func):
    """Decorator to ensure view returns JSON response."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, dict):
            return JsonResponse(result)
        return result
    return wrapper
