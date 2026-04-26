"""
Utilitaires communs
"""
import logging

logger = logging.getLogger(__name__)

def log_action(user, action, object_type, object_id, details=None):
    """Logger une action utilisateur"""
    message = f"User {user.id} performed {action} on {object_type} {object_id}"
    if details:
        message += f": {details}"
    logger.info(message)
