"""
Custom validators for the application.
"""

from django.core.exceptions import ValidationError


def validate_positive_number(value):
    """Validate that a number is positive."""
    if value < 0:
        raise ValidationError("This field must be a positive number.")
