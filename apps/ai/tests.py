from django.test import TestCase
from .models import SystemeIA


class SystemeIATestCase(TestCase):
    """Tests pour le modèle SystemeIA"""
    
    def setUp(self):
        """Initialisation des données de test"""
        self.systeme = SystemeIA.objects.create(
            nom="Nutrition AI",
            version="1.0",
            est_actif=True
        )
    
    def test_creation_systeme_ia(self):
        """Teste la création d'un système IA"""
        self.assertEqual(self.systeme.nom, "Nutrition AI")
        self.assertEqual(self.systeme.version, "1.0")
        self.assertTrue(self.systeme.est_actif)
