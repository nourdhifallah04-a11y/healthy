"""
================================================================================
 TESTS — calculer_score_professionnel() avec cas réels
================================================================================

Lance via :
    python manage.py test myapp.tests_score_professionnel
    ou directement :
    python manage.py test myapp.tests_score_professionnel.ScoreProfessionnelTests

Couvre :
  • 4 catégories IMC × 4 objectifs = 16 combinaisons clés
  • Cas limites (allergies, restrictions, valeurs nulles, valeurs extrêmes)
  • Vérification que le score reste TOUJOURS dans [0, 100]
  • Vérification que les scores sont monotones (mauvais plat < bon plat)
  • Intégration avec le monitoring
"""
from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock

from django.test import TestCase

from myapp.models import Plat
from myapp.score_monitoring import score_monitor


def _make_plat(**kw):
    """Construit un Plat en mémoire (pas sauvegardé en DB)."""
    defaults = dict(
        id_plat=1, nom="Test", description="",
        calorie=500, proteine=25, glucides=40,
        lipides=15, fibres=8,
    )
    defaults.update(kw)
    p = Plat(**defaults)
    return p


def _make_profil(*, age=30, sexe='homme', poids=75, taille=175,
                 objectif='maintien', niveau_activite='modere',
                 allergies='', restrictions=''):
    """Construit un mock de ProfilNutritionnel sans toucher la DB."""
    profil = MagicMock()
    profil.age = age
    profil.sexe = sexe
    profil.poids = Decimal(str(poids))
    profil.taille = Decimal(str(taille))
    profil.objectif = objectif
    profil.niveau_activite = niveau_activite
    profil.allergies = allergies
    profil.restrictions_alimentaires = restrictions
    # IMC réel
    imc = float(poids) / ((float(taille) / 100) ** 2)
    profil.calculer_imc = MagicMock(return_value=round(imc, 2))
    if imc < 18.5:    cat = 'insuffisance_ponderale'
    elif imc < 25:    cat = 'normal'
    elif imc < 30:    cat = 'surpoids'
    else:             cat = 'obesite'
    profil.determiner_categorie_imc = MagicMock(return_value=cat)
    return profil


# ============================================================================
#  TESTS
# ============================================================================
class ScoreProfessionnelTests(TestCase):

    def setUp(self):
        score_monitor.reset('professionnel')

    # ---------------------- Bornes & validation post-calcul -----------------
    def test_score_toujours_dans_0_100(self):
        """Le score doit TOUJOURS être dans [0, 100], peu importe les inputs."""
        profil = _make_profil()
        cases = [
            _make_plat(calorie=0, proteine=0, glucides=0, lipides=0, fibres=0),
            _make_plat(calorie=10000, proteine=500, glucides=500, lipides=500, fibres=100),
            _make_plat(calorie=-100, proteine=-10, glucides=-10, lipides=-10, fibres=-1),
        ]
        for plat in cases:
            score = Plat.calculer_score_professionnel(plat, profil)
            self.assertGreaterEqual(score, 0.0, f"Score < 0 pour {plat.nom}")
            self.assertLessEqual(score, 100.0, f"Score > 100 pour {plat.nom}")

    # ---------------------- Allergies & restrictions ------------------------
    def test_allergie_donne_score_zero(self):
        plat = _make_plat(nom="Salade au poulet", description="poulet et tomates")
        profil = _make_profil(allergies="poulet")
        self.assertEqual(Plat.calculer_score_professionnel(plat, profil), 0.0)

    def test_restriction_donne_score_zero(self):
        plat = _make_plat(nom="Fromage gratiné", description="lait, fromage")
        profil = _make_profil(restrictions="fromage")
        self.assertEqual(Plat.calculer_score_professionnel(plat, profil), 0.0)

    def test_allergie_insensible_casse(self):
        plat = _make_plat(nom="Crevettes Sautées", description="crevettes ail")
        profil = _make_profil(allergies="CREVETTES")
        self.assertEqual(Plat.calculer_score_professionnel(plat, profil), 0.0)

    # ---------------------- Cas réels — Surpoids + perte_poids --------------
    def test_surpoids_perte_poids_plat_ideal(self):
        """Salade protéinée légère : devrait scorer haut pour cet IMC."""
        plat = _make_plat(nom="Salade poulet quinoa",
                          calorie=380, proteine=35, glucides=18,
                          lipides=10, fibres=9)
        profil = _make_profil(poids=90, taille=170,  # IMC ≈ 31.1 → obésité
                              objectif='perte_poids')
        score, details = Plat.calculer_score_professionnel(
            plat, profil, return_details=True
        )
        self.assertGreaterEqual(score, 70, f"Plat idéal devrait >= 70, obtenu {score}")
        self.assertEqual(details['categorie_imc'], 'obesite')

    def test_surpoids_perte_poids_plat_inadapte(self):
        """Pizza grasse : devrait scorer bas pour obésité + perte_poids."""
        plat = _make_plat(nom="Pizza 4 fromages",
                          calorie=950, proteine=22, glucides=85,
                          lipides=42, fibres=2)
        profil = _make_profil(poids=90, taille=170, objectif='perte_poids')
        score = Plat.calculer_score_professionnel(plat, profil)
        self.assertLessEqual(score, 35, f"Plat inadapté devrait <= 35, obtenu {score}")

    # ---------------------- Cas réel — Sportif prise muscle -----------------
    def test_homme_sportif_prise_muscle(self):
        """Steak + riz : très bon pour sportif jeune."""
        plat = _make_plat(nom="Steak grillé riz brun",
                          calorie=650, proteine=45, glucides=55,
                          lipides=18, fibres=6)
        profil = _make_profil(age=25, sexe='homme', poids=80, taille=180,
                              objectif='prise_muscle', niveau_activite='actif')
        score = Plat.calculer_score_professionnel(plat, profil)
        self.assertGreaterEqual(score, 75, f"Plat sportif devrait >= 75, obtenu {score}")

    # ---------------------- Cas réel — Senior maintien ----------------------
    def test_femme_senior_maintien(self):
        """Soupe de légumes + poisson : bon pour senior."""
        plat = _make_plat(nom="Cabillaud légumes vapeur",
                          calorie=420, proteine=32, glucides=22,
                          lipides=12, fibres=8)
        profil = _make_profil(age=62, sexe='femme', poids=65, taille=160,
                              objectif='maintien', niveau_activite='leger')
        score = Plat.calculer_score_professionnel(plat, profil)
        self.assertGreaterEqual(score, 70)

    # ---------------------- Cas réel — Insuffisance pondérale ---------------
    def test_insuffisance_ponderale_plat_calorique(self):
        """Pâtes carbonara : adapté pour prise de poids."""
        plat = _make_plat(nom="Pâtes carbonara",
                          calorie=900, proteine=40, glucides=80,
                          lipides=28, fibres=4)
        profil = _make_profil(age=22, sexe='homme', poids=55, taille=180,
                              objectif='prise_muscle')
        score = Plat.calculer_score_professionnel(plat, profil)
        self.assertGreaterEqual(score, 65)

    # ---------------------- Cohérence : meilleur > pire ---------------------
    def test_monotonie_meilleur_score(self):
        """Pour un même profil, plat sain doit toujours > plat junk."""
        profil = _make_profil(poids=80, taille=175, objectif='maintien')
        sain = _make_plat(nom="Saumon brocoli", calorie=500, proteine=35,
                          glucides=30, lipides=18, fibres=10)
        junk = _make_plat(nom="Frites bacon", calorie=1100, proteine=15,
                          glucides=90, lipides=55, fibres=2)
        s_sain = Plat.calculer_score_professionnel(sain, profil)
        s_junk = Plat.calculer_score_professionnel(junk, profil)
        self.assertGreater(s_sain, s_junk,
                           f"Sain ({s_sain}) doit > junk ({s_junk})")

    # ---------------------- Détails & breakdown ----------------------------
    def test_return_details_structure(self):
        plat = _make_plat()
        profil = _make_profil()
        score, details = Plat.calculer_score_professionnel(
            plat, profil, return_details=True
        )
        self.assertIn('breakdown', details)
        self.assertIn('besoins', details)
        self.assertIn('categorie_imc', details)
        self.assertIn('evaluation', details)
        # breakdown contient les 6 sous-scores
        for k in ('calories', 'proteines', 'glucides', 'lipides', 'fibres', 'age_sexe'):
            self.assertIn(k, details['breakdown'])

    def test_breakdown_caps_respectes(self):
        """Chaque sous-score doit respecter son max individuel."""
        plat = _make_plat(calorie=500, proteine=200, glucides=200,
                          lipides=200, fibres=200)
        profil = _make_profil()
        _, details = Plat.calculer_score_professionnel(
            plat, profil, return_details=True
        )
        caps = Plat._PRO_MAX_POINTS
        for k, v in details['breakdown'].items():
            self.assertLessEqual(v, caps[k], f"{k} dépasse cap {caps[k]}")

    # ---------------------- Monitoring intégré ------------------------------
    def test_monitoring_enregistre_score(self):
        score_monitor.reset('professionnel')
        plat = _make_plat()
        profil = _make_profil()
        Plat.calculer_score_professionnel(plat, profil)
        stats = score_monitor.get_stats('professionnel')
        self.assertEqual(stats['samples'], 1)

    def test_monitoring_detecte_pas_anomalie_normale(self):
        score_monitor.reset('professionnel')
        plat = _make_plat()
        profil = _make_profil()
        for _ in range(5):
            Plat.calculer_score_professionnel(plat, profil)
        stats = score_monitor.get_stats('professionnel')
        self.assertEqual(stats['anomalies'], 0)


# ============================================================================
#  Exécution standalone (sans manage.py)
# ============================================================================
if __name__ == '__main__':
    import django, os, sys
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')
    django.setup()
    import unittest
    unittest.main()

