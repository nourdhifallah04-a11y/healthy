"""
Tests de performance
"""
import pytest
from django.test.utils import override_settings

@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_score_calculation_performance(user, nutritional_profile):
    """Test de performance du calcul de scores"""
    from apps.scoring.services import ScoreCalculator
    from django.test.utils import override_settings
    from django.db import connection
    from django.test.utils import CaptureQueriesContext
    
    with CaptureQueriesContext(connection) as context:
        score = ScoreCalculator.calculate_professional_score(user)
    
    # Vérifier que le nombre de requêtes est acceptable
    assert len(context.captured_queries) < 10
    assert 0 <= score <= 100
