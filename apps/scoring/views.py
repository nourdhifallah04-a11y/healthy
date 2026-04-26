"""
Vues pour l'app scoring
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Score, Recommendation
from .serializers import ScoreSerializer, RecommendationSerializer
from .services import ScoreCalculator, ScoreMonitoring

class ScoreViewSet(viewsets.ModelViewSet):
    """ViewSet pour les scores"""
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Score.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """Calculer les scores"""
        score_type = request.data.get('score_type')
        
        if score_type == 'professional':
            value = ScoreCalculator.calculate_professional_score(request.user)
        else:
            return Response(
                {'error': 'Unknown score type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        score, created = Score.objects.update_or_create(
            user=request.user,
            score_type=score_type,
            defaults={'value': value}
        )
        
        return Response(ScoreSerializer(score).data)

class RecommendationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les recommandations"""
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Recommendation.objects.filter(user=self.request.user)
