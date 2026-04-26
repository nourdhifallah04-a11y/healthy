"""
Middlewares personnalisés
"""
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware:
    """Middleware pour la gestion centralisée des erreurs"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_exception(self, request, exception):
        """Traiter les exceptions"""
        logger.error(f"Error processing {request.path}: {str(exception)}")
        return JsonResponse({
            'error': 'Internal server error',
            'message': str(exception)
        }, status=500)
