from myapp.menu.serializers import MenuSerializer
from myapp.systemeIA.serializers import SystemeIASerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from myapp.users.models import Client
from myapp.systemeIA.models import SystemeIA


# ===== API ViewSets =====

class SystemeIAViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour le système IA de recommandation de menus.
    Permet de consulter les recommandations et analyser les préférences.
    """
    queryset = SystemeIA.objects.filter(est_actif=True)
    serializer_class = SystemeIASerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def recommandations(self, request):
        """Récupère les recommandations de menus personnalisées pour un client"""
        client_id = request.query_params.get('client_id')
        if not client_id:
            return Response(
                {'error': 'client_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            client = Client.objects.get(id=client_id)
            ia_system = SystemeIA.objects.filter(est_actif=True).first()
            
            if not ia_system:
                return Response(
                    {'error': 'Système IA non disponible'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            recommandations = ia_system.recommander_menus(client)
            serializer = MenuSerializer(recommandations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Client.DoesNotExist:
            return Response(
                {'error': 'Client non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def analyser_preferences(self, request):
        """Analyse les préférences alimentaires d'un client"""
        client_id = request.query_params.get('client_id')
        if not client_id:
            return Response(
                {'error': 'client_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            client = Client.objects.get(id=client_id)
            ia_system = SystemeIA.objects.filter(est_actif=True).first()
            
            if not ia_system:
                return Response(
                    {'error': 'Système IA non disponible'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            preferences = ia_system.analyser_preferences(client)
            return Response(preferences, status=status.HTTP_200_OK)
        except Client.DoesNotExist:
            return Response(
                {'error': 'Client non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )

