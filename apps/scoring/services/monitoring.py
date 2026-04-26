"""
Service de monitoring des scores
"""
import logging
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)

class ScoreMonitoring:
    """Classe pour monitorer les scores"""
    
    @staticmethod
    def check_score_degradation(user, days=7):
        """Vérifier la dégradation des scores"""
        from .models import Score
        
        cutoff_date = timezone.now() - timedelta(days=days)
        recent_scores = Score.objects.filter(
            user=user,
            created_at__gte=cutoff_date
        ).values('score_type').distinct()
        
        degradations = []
        for score_entry in recent_scores:
            score_type = score_entry['score_type']
            scores = Score.objects.filter(
                user=user,
                score_type=score_type
            ).order_by('-created_at')[:2]
            
            if len(scores) == 2:
                if scores[0].value < scores[1].value:
                    degradations.append({
                        'type': score_type,
                        'current': scores[0].value,
                        'previous': scores[1].value,
                    })
                    logger.warning(
                        f"Score degradation for {user.username}: "
                        f"{score_type} from {scores[1].value} to {scores[0].value}"
                    )
        
        return degradations
