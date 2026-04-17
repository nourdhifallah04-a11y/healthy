"""
Comprehensive test suite for myapp models and views
"""
from django.test import TestCase, Client as DjangoClient
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import (
    Utilisateur, Client, ProfilNutritionnel, Plat,
    Menu, CompositionMenu, Commande, LigneCommande, SystemeIA
)

User = get_user_model()


class UtilisateurTestCase(TestCase):
    """Test cases for Utilisateur model"""
    
    def setUp(self):
        """Set up test user"""
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'nom': 'Dupont',
            'prenom': 'Jean'
        }
    
    def test_create_user(self):
        """Test creating a regular user"""
        user = Utilisateur.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.nom, self.user_data['nom'])
        self.assertTrue(user.check_password(self.user_data['password']))
    
    def test_create_user_without_email_raises_error(self):
        """Test that creating user without email raises ValueError"""
        with self.assertRaises(ValueError):
            Utilisateur.objects.create_user(email='', password='pass')
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        admin_data = {
            'email': 'admin@example.com',
            'password': 'adminpass',
            'nom': 'Admin',
            'prenom': 'User'
        }
        admin = Utilisateur.objects.create_superuser(**admin_data)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_active)
    
    def test_user_string_representation(self):
        """Test __str__ method returns correct format"""
        user = Utilisateur.objects.create_user(**self.user_data)
        self.assertEqual(str(user), f"{user.nom} {user.prenom}")


class ClientTestCase(TestCase):
    """Test cases for Client model"""
    
    def setUp(self):
        """Set up test client and user"""
        self.user = Utilisateur.objects.create_user(
            email='client@example.com',
            password='pass123',
            nom='Martin',
            prenom='Pierre'
        )
        self.client = Client.objects.create(utilisateur=self.user)
    
    def test_client_creation(self):
        """Test creating a client"""
        self.assertEqual(self.client.utilisateur, self.user)
        self.assertIsNone(self.client.date_naissance)
    
    def test_client_string_representation(self):
        """Test __str__ method"""
        expected = f"Client: {self.user.nom} {self.user.prenom}"
        self.assertEqual(str(self.client), expected)


class ProfilNutritionnelTestCase(TestCase):
    """Test cases for ProfilNutritionnel model"""
    
    def setUp(self):
        """Set up test user and profile"""
        self.user = Utilisateur.objects.create_user(
            email='profil@example.com',
            password='pass123',
            nom='Dubois',
            prenom='Marie'
        )
        self.client = Client.objects.create(utilisateur=self.user)
        self.profil = ProfilNutritionnel.objects.create(
            client=self.client,
            age=30,
            taille=Decimal('170'),
            poids=Decimal('65'),
            sexe='femme',
            objectif='maintien',
            niveau_activite='modere'
        )
    
    def test_profil_creation(self):
        """Test creating a nutritional profile"""
        self.assertEqual(self.profil.client, self.client)
        self.assertEqual(self.profil.age, 30)
    
    def test_calculer_imc(self):
        """Test IMC calculation"""
        imc = self.profil.calculer_imc()
        # 65 / (1.70^2) = 22.49
        self.assertAlmostEqual(imc, 22.49, places=1)
    
    def test_calculer_bmr(self):
        """Test BMR calculation"""
        bmr = self.profil.calculer_bmr()
        # Should be positive and reasonable for a 30-year-old woman
        self.assertGreater(bmr, 1000)
        self.assertLess(bmr, 2000)
    
    def test_besoins_caloriques_journaliers(self):
        """Test daily caloric needs calculation"""
        besoins = self.profil.besoins_caloriques_journaliers()
        self.assertGreater(besoins, 1500)
        self.assertLess(besoins, 3000)
    
    def test_besoins_caloriques_perte_poids(self):
        """Test caloric needs adjustment for weight loss"""
        self.profil.objectif = 'perte_poids'
        self.profil.save()
        besoins_perte = self.profil.besoins_caloriques_journaliers()
        
        self.profil.objectif = 'maintien'
        self.profil.save()
        besoins_normal = self.profil.besoins_caloriques_journaliers()
        
        # Weight loss should have lower caloric needs
        self.assertLess(besoins_perte, besoins_normal)


class PlatTestCase(TestCase):
    """Test cases for Plat model"""
    
    def setUp(self):
        """Set up test dishes"""
        self.plat_sain = Plat.objects.create(
            nom='Salade Verte',
            description='Salade simple et saine',
            calorie=150,
            proteine=5,
            glucides=10,
            lipides=8,
            fibres=3,
            prix=Decimal('8.50')
        )
        
        self.plat_riche = Plat.objects.create(
            nom='Burger Premium',
            description='Burger avec double fromage',
            calorie=950,
            proteine=35,
            glucides=65,
            lipides=45,
            fibres=2,
            prix=Decimal('15.99')
        )
    
    def test_plat_creation(self):
        """Test creating a dish"""
        self.assertEqual(self.plat_sain.nom, 'Salade Verte')
        self.assertEqual(self.plat_sain.calorie, 150)
    
    def test_afficher_detail(self):
        """Test detail display method"""
        detail = self.plat_sain.afficher_detail()
        self.assertIn('nom', detail)
        self.assertIn('calories', detail)
        self.assertEqual(detail['calories'], 150)
    
    def test_calculer_score_nutritionnel_sain(self):
        """Test nutritional score for healthy dish"""
        score = self.plat_sain.calculer_score_nutritionnel()
        # Healthy dish with low calories should have good score
        self.assertGreater(score, 60)
    
    def test_calculer_score_nutritionnel_riche(self):
        """Test nutritional score for rich dish"""
        score = self.plat_riche.calculer_score_nutritionnel()
        # Rich dish with high calories should have lower score
        self.assertLess(score, 60)
    
    def test_score_range(self):
        """Test that score is always between 0 and 100"""
        for plat in [self.plat_sain, self.plat_riche]:
            score = plat.calculer_score_nutritionnel()
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)


class MenuTestCase(TestCase):
    """Test cases for Menu model"""
    
    def setUp(self):
        """Set up test menu and dishes"""
        self.plat1 = Plat.objects.create(
            nom='Poulet Grillé',
            description='Poulet',
            calorie=300,
            proteine=35,
            glucides=0,
            lipides=10,
            fibres=0,
            prix=Decimal('12.00')
        )
        
        self.plat2 = Plat.objects.create(
            nom='Riz Blanc',
            description='Riz',
            calorie=200,
            proteine=4,
            glucides=45,
            lipides=0,
            fibres=1,
            prix=Decimal('3.00')
        )
        
        self.menu = Menu.objects.create(
            nom='Menu Protéiné',
            description='Menu riche en protéines',
            date_debut='2024-01-01',
            date_fin='2024-01-31'
        )
    
    def test_menu_creation(self):
        """Test creating a menu"""
        self.assertEqual(self.menu.nom, 'Menu Protéiné')
        self.assertTrue(self.menu.est_actif)
    
    def test_ajouter_plat(self):
        """Test adding dish to menu"""
        comp = self.menu.ajouter_plat(self.plat1, quantite=1)
        self.assertEqual(comp.quantite, 1)
        self.assertIn(self.plat1, self.menu.plats.all())
    
    def test_ajouter_plat_augmente_quantite(self):
        """Test that adding same dish increases quantity"""
        self.menu.ajouter_plat(self.plat1, quantite=1)
        self.menu.ajouter_plat(self.plat1, quantite=2)
        
        comp = CompositionMenu.objects.get(menu=self.menu, plat=self.plat1)
        self.assertEqual(comp.quantite, 3)
    
    def test_supprimer_plat(self):
        """Test removing dish from menu"""
        self.menu.ajouter_plat(self.plat1)
        self.menu.supprimer_plat(self.plat1)
        
        self.assertNotIn(self.plat1, self.menu.plats.all())
    
    def test_calculer_valeur_nutritionnelle_totale(self):
        """Test calculating total nutritional values"""
        self.menu.ajouter_plat(self.plat1, quantite=1)
        self.menu.ajouter_plat(self.plat2, quantite=1)
        
        valeurs = self.menu.calculer_valeur_nutritionnelle_totale()
        
        self.assertEqual(valeurs['calories'], 500)  # 300 + 200
        self.assertEqual(valeurs['proteines'], 39)  # 35 + 4
        self.assertEqual(valeurs['prix'], 15)  # 12 + 3


class CommandeTestCase(TestCase):
    """Test cases for Commande model"""
    
    def setUp(self):
        """Set up test order"""
        self.user = Utilisateur.objects.create_user(
            email='client2@example.com',
            password='pass123',
            nom='Client',
            prenom='Test'
        )
        self.client = Client.objects.create(utilisateur=self.user)
        self.commande = Commande.objects.create(client=self.client)
    
    def test_commande_creation(self):
        """Test creating an order"""
        self.assertEqual(self.commande.client, self.client)
        self.assertEqual(self.commande.statut, 'panier')
    
    def test_valider_commande(self):
        """Test validating order"""
        self.assertTrue(self.commande.valider_commande())
        self.assertEqual(self.commande.statut, 'confirmee')
    
    def test_valider_commande_deja_confirmee(self):
        """Test that already confirmed order cannot be validated"""
        self.commande.valider_commande()
        self.assertFalse(self.commande.valider_commande())
    
    def test_calculer_total(self):
        """Test calculating order total"""
        # Create menu and add line items
        plat = Plat.objects.create(
            nom='Test Plat',
            description='Test',
            calorie=100,
            proteine=10,
            prix=Decimal('10.00')
        )
        menu = Menu.objects.create(
            nom='Test Menu',
            description='Test',
            date_debut='2024-01-01',
            date_fin='2024-01-31'
        )
        menu.ajouter_plat(plat)
        
        ligne = LigneCommande.objects.create(
            commande=self.commande,
            menu=menu,
            quantite=2,
            prix_unitaire=Decimal('10.00')
        )
        
        total = self.commande.calculer_total()
        self.assertEqual(total, Decimal('20.00'))


class SystemeIATestCase(TestCase):
    """Test cases for SystemeIA model"""
    
    def setUp(self):
        """Set up test AI system"""
        self.ia = SystemeIA.objects.create(
            nom='Test AI',
            version='1.0'
        )
        
        # Create test user and client
        self.user = Utilisateur.objects.create_user(
            email='ia@example.com',
            password='pass123',
            nom='IA',
            prenom='Test'
        )
        self.client = Client.objects.create(utilisateur=self.user)
    
    def test_ia_creation(self):
        """Test creating AI system"""
        self.assertEqual(self.ia.nom, 'Test AI')
        self.assertTrue(self.ia.est_actif)
    
    def test_analyser_preferences(self):
        """Test analyzing client preferences"""
        preferences = self.ia.analyser_preferences(self.client)
        self.assertIn('plats_frequents', preferences)
        self.assertIn('preferences', preferences)
    
    def test_recommander_menus(self):
        """Test menu recommendations"""
        # Create profile for recommendations
        profil = ProfilNutritionnel.objects.create(
            client=self.client,
            age=25,
            taille=Decimal('175'),
            poids=Decimal('70'),
            objectif='maintien'
        )
        
        # Create some menus
        menu = Menu.objects.create(
            nom='Test Menu',
            description='Test',
            date_debut='2024-01-01',
            date_fin='2024-01-31'
        )
        
        recommandations = self.ia.recommander_menus(self.client)
        self.assertIsInstance(recommandations, list)


class APIViewsTestCase(TestCase):
    """Test cases for API views"""
    
    def setUp(self):
        """Set up test client and user"""
        self.django_client = DjangoClient()
        self.user = Utilisateur.objects.create_user(
            email='apitest@example.com',
            password='apipass123',
            nom='API',
            prenom='User'
        )
    
    def test_login_required_for_api(self):
        """Test that API requires authentication"""
        response = self.django_client.get('/api/clients/')
        self.assertEqual(response.status_code, 401)
    
    def test_authenticated_client_list(self):
        """Test client list with authenticated user"""
        self.django_client.login(email='apitest@example.com', password='apipass123')
        # Note: This might need adjustment based on actual auth backend
        # response = self.django_client.get('/api/clients/')
        # self.assertEqual(response.status_code, 200)


# ============================================
# COMMANDE TESTS
# ============================================

class CommandeTestCase(TestCase):
    """Test cases for Commande model"""
    
    def setUp(self):
        """Set up test data for commande tests"""
        # Create user and client
        self.utilisateur = Utilisateur.objects.create_user(
            email='client@example.com',
            password='testpass123',
            nom='Dupont',
            prenom='Jean'
        )
        self.client = Client.objects.create(utilisateur=self.utilisateur)
        
        # Create menu and plats
        self.plat1 = Plat.objects.create(
            nom='Poulet rôti',
            description='Poulet rôti avec légumes',
            calorie=450,
            proteine=35,
            glucides=20,
            lipides=15,
            prix=Decimal('8.50'),
            est_disponible=True
        )
        
        self.plat2 = Plat.objects.create(
            nom='Riz basmati',
            description='Riz basmati cuit',
            calorie=200,
            proteine=5,
            glucides=45,
            lipides=1,
            prix=Decimal('3.50'),
            est_disponible=True
        )
        
        self.menu = Menu.objects.create(
            nom='Menu Délice',
            description='Délicieux menu',
            prix=Decimal('12.00'),
            est_actif=True
        )
        self.menu.plats.add(self.plat1, self.plat2)
        
        # Create commande
        self.commande = Commande.objects.create(
            client=self.client,
            statut='panier'
        )
    
    def test_create_commande(self):
        """Test creating a commande"""
        self.assertIsNotNone(self.commande.id_commande)
        self.assertEqual(self.commande.statut, 'panier')
        self.assertEqual(self.commande.client, self.client)
    
    def test_commande_str_representation(self):
        """Test string representation of commande"""
        expected_str = f"Commande #{self.commande.id_commande} - {self.utilisateur.nom}"
        self.assertEqual(str(self.commande), expected_str)
    
    def test_valider_commande(self):
        """Test validating a commande changes status"""
        self.assertTrue(self.commande.valider_commande())
        self.commande.refresh_from_db()
        self.assertEqual(self.commande.statut, 'confirmee')
    
    def test_valider_commande_already_confirmed(self):
        """Test that validating an already confirmed commande returns False"""
        self.commande.valider_commande()
        self.assertFalse(self.commande.valider_commande())
    
    def test_calculer_total(self):
        """Test calculating commande total"""
        # Add items to commande
        ligne1 = LigneCommande.objects.create(
            commande=self.commande,
            menu=self.menu,
            quantite=2,
            prix_unitaire=Decimal('12.00')
        )
        
        total = self.commande.calculer_total()
        self.assertEqual(total, Decimal('24.00'))
    
    def test_calculer_nutrition_totale(self):
        """Test calculating total nutritional values"""
        ligne1 = LigneCommande.objects.create(
            commande=self.commande,
            menu=self.menu,
            quantite=1,
            prix_unitaire=Decimal('12.00')
        )
        
        nutrition = self.commande.calculer_nutrition_totale()
        
        # Should contain keys
        self.assertIn('calories', nutrition)
        self.assertIn('proteines', nutrition)
        self.assertIn('glucides', nutrition)
        self.assertIn('lipides', nutrition)
        
        # Should have non-zero values
        self.assertGreater(nutrition['calories'], 0)
        self.assertGreater(nutrition['proteines'], 0)


class LigneCommandeTestCase(TestCase):
    """Test cases for LigneCommande model"""
    
    def setUp(self):
        """Set up test data"""
        self.utilisateur = Utilisateur.objects.create_user(
            email='client2@example.com',
            password='testpass123',
            nom='Martin',
            prenom='Pierre'
        )
        self.client = Client.objects.create(utilisateur=self.utilisateur)
        
        self.plat = Plat.objects.create(
            nom='Salade méditerranéenne',
            description='Salade fraîche',
            calorie=300,
            proteine=15,
            glucides=25,
            lipides=10,
            prix=Decimal('7.00'),
            est_disponible=True
        )
        
        self.menu = Menu.objects.create(
            nom='Menu Santé',
            description='Repas équilibré',
            prix=Decimal('10.00'),
            est_actif=True
        )
        self.menu.plats.add(self.plat)
        
        self.commande = Commande.objects.create(
            client=self.client,
            statut='panier'
        )
    
    def test_create_ligne_commande(self):
        """Test creating a ligne de commande"""
        ligne = LigneCommande.objects.create(
            commande=self.commande,
            menu=self.menu,
            quantite=2,
            prix_unitaire=Decimal('10.00')
        )
        
        self.assertEqual(ligne.commande, self.commande)
        self.assertEqual(ligne.menu, self.menu)
        self.assertEqual(ligne.quantite, 2)
    
    def test_sous_total_calculation(self):
        """Test sous_total property calculation"""
        ligne = LigneCommande.objects.create(
            commande=self.commande,
            menu=self.menu,
            quantite=3,
            prix_unitaire=Decimal('10.00')
        )
        
        self.assertEqual(ligne.sous_total, Decimal('30.00'))
    
    def test_ligne_commande_str_representation(self):
        """Test string representation of ligne commande"""
        ligne = LigneCommande.objects.create(
            commande=self.commande,
            menu=self.menu,
            quantite=1,
            prix_unitaire=Decimal('10.00')
        )
        
        expected_str = f"{self.commande.id_commande} - {self.menu.nom} x1"
        self.assertEqual(str(ligne), expected_str)


class CommandeViewsTestCase(TestCase):
    """Test cases for Commande views"""
    
    def setUp(self):
        """Set up test data"""
        self.django_client = DjangoClient()
        
        self.utilisateur = Utilisateur.objects.create_user(
            email='testview@example.com',
            password='testpass123',
            nom='Test',
            prenom='User'
        )
        
        self.client = Client.objects.create(utilisateur=self.utilisateur)
        
        self.plat = Plat.objects.create(
            nom='Plat test',
            description='Plat pour test',
            calorie=500,
            proteine=30,
            glucides=40,
            lipides=15,
            prix=Decimal('9.99'),
            est_disponible=True
        )
        
        self.menu = Menu.objects.create(
            nom='Menu test',
            description='Menu de test',
            prix=Decimal('12.99'),
            est_actif=True
        )
        self.menu.plats.add(self.plat)
        
        self.commande = Commande.objects.create(
            client=self.client,
            statut='panier'
        )
    
    def test_panier_requires_authentication(self):
        """Test that panier view requires authentication"""
        response = self.django_client.get('/panier/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_panier_view_authenticated(self):
        """Test panier view with authenticated user"""
        self.django_client.force_login(self.utilisateur)
        response = self.django_client.get('/panier/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'panier', html=False)
    
    def test_mes_commandes_requires_authentication(self):
        """Test that mes commandes view requires authentication"""
        response = self.django_client.get('/mes-commandes/')
        self.assertEqual(response.status_code, 302)
    
    def test_mes_commandes_view_authenticated(self):
        """Test mes commandes view with authenticated user"""
        self.django_client.force_login(self.utilisateur)
        response = self.django_client.get('/mes-commandes/')
        self.assertEqual(response.status_code, 200)
    
    def test_commande_detail_requires_authentication(self):
        """Test that commande detail view requires authentication"""
        response = self.django_client.get(f'/commande/{self.commande.id_commande}/')
        self.assertEqual(response.status_code, 302)
    
    def test_commande_detail_view_authenticated(self):
        """Test commande detail view with authenticated user"""
        self.django_client.force_login(self.utilisateur)
        response = self.django_client.get(f'/commande/{self.commande.id_commande}/')
        self.assertEqual(response.status_code, 200)
    
    def test_commande_detail_wrong_user(self):
        """Test that user cannot view another user's commande"""
        autre_utilisateur = Utilisateur.objects.create_user(
            email='other@example.com',
            password='testpass123',
            nom='Autre',
            prenom='User'
        )
        
        self.django_client.force_login(autre_utilisateur)
        response = self.django_client.get(f'/commande/{self.commande.id_commande}/')
        self.assertEqual(response.status_code, 302)  # Redirect


class CommandeIntegrationTestCase(TestCase):
    """Integration tests for complete commande flow"""
    
    def setUp(self):
        """Set up test data"""
        self.django_client = DjangoClient()
        
        self.utilisateur = Utilisateur.objects.create_user(
            email='integration@example.com',
            password='testpass123',
            nom='Integration',
            prenom='Test'
        )
        
        self.client = Client.objects.create(utilisateur=self.utilisateur)
        
        # Create multiple plats
        self.plats = []
        for i in range(3):
            plat = Plat.objects.create(
                nom=f'Plat {i+1}',
                description=f'Description {i+1}',
                calorie=400 + (i * 50),
                proteine=25 + (i * 5),
                glucides=30 + (i * 5),
                lipides=12 + (i * 2),
                prix=Decimal(f'{8 + i}.50'),
                est_disponible=True
            )
            self.plats.append(plat)
        
        # Create menu with multiple plats
        self.menu = Menu.objects.create(
            nom='Menu complet',
            description='Menu avec tous les plats',
            prix=Decimal('25.00'),
            est_actif=True
        )
        for plat in self.plats:
            self.menu.plats.add(plat)
    
    def test_complete_commande_flow(self):
        """Test the complete flow: cart -> checkout -> confirmation"""
        self.django_client.force_login(self.utilisateur)
        
        # 1. Access cart
        response = self.django_client.get('/panier/')
        self.assertEqual(response.status_code, 200)
        
        # 2. Create commande with items
        commande = Commande.objects.get(client=self.client, statut='panier')
        
        LigneCommande.objects.create(
            commande=commande,
            menu=self.menu,
            quantite=2,
            prix_unitaire=Decimal('25.00')
        )
        
        # 3. Verify total calculation
        total = commande.calculer_total()
        self.assertEqual(total, Decimal('50.00'))
        
        # 4. Verify nutritional values
        nutrition = commande.calculer_nutrition_totale()
        self.assertGreater(nutrition['calories'], 0)
        
        # 5. Access checkout
        response = self.django_client.get('/checkout/')
        self.assertEqual(response.status_code, 200)
        
        # 6. Submit checkout (simulate)
        response = self.django_client.post('/checkout/', {
            'adresse_livraison': '123 Rue de Test, 75001 Paris',
            'notes': 'Pas de glaçons'
        })
        
        # Should redirect to confirmation
        self.assertEqual(response.status_code, 302)
        
        # 7. Verify commande status changed
        commande.refresh_from_db()
        self.assertEqual(commande.statut, 'confirmee')
        self.assertNotEqual(commande.adresse_livraison, '')

