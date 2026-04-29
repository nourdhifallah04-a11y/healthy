from myapp.profilNutritionnel.models import ProfilNutritionnel
from myapp.profilNutritionnel.serializers import ProfilNutritionnelSerializer
from rest_framework import status, generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect
from django.conf import settings
import logging
from myapp.users.models import Client
from myapp.plat.models import Plat
from myapp.plat.serializers import PlatRecommandationSerializer

logger = logging.getLogger(__name__)

# ===== Configuration Timeout N8N =====
N8N_WEBHOOK_TIMEOUT = getattr(settings, 'N8N_WEBHOOK_TIMEOUT', 600)  # Default: 120 secondes
N8N_WEBHOOK_URL = getattr(settings, 'N8N_WEBHOOK_URL', 'http://192.168.1.184:5678/webhook/reco-nutrition')

# ===== Async Jobs Cache =====
# Dictionnaire pour stocker les résultats des jobs async
# Clé: job_id, Valeur: {'status': 'pending|completed|failed', 'result': {...}, 'error': {...}, 'timestamp': datetime}
async_jobs_cache = {}


# ===== Profile Views =====

class CreerProfilNutritionnelView(generics.CreateAPIView):
    """Vue API pour créer un profil nutritionnel pour l'utilisateur courant"""
    serializer_class = ProfilNutritionnelSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Crée ou met à jour le profil nutritionnel de l'utilisateur connecté"""
        try:
            # Récupérer le client de l'utilisateur courant
            utilisateur = request.user
            client = Client.objects.get(utilisateur=utilisateur)
            
            # Ajouter le client aux données
            data = request.data.copy()
            data['client'] = client.id
            
            # Créer ou mettre à jour le profil
            try:
                profil = ProfilNutritionnel.objects.get(client=client)
                serializer = self.get_serializer(profil, data=data, partial=True)
            except ProfilNutritionnel.DoesNotExist:
                serializer = self.get_serializer(data=data)
            
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            return Response({
                'success': True,
                'message': 'Profil nutritionnel créé avec succès',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        except Client.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Client non trouvé pour cet utilisateur'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_create(self, serializer):
        serializer.save()


class ObtenirProfilNutritionnelView(generics.RetrieveAPIView):
    """Vue pour récupérer le profil nutritionnel de l'utilisateur courant"""
    serializer_class = ProfilNutritionnelSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        try:
            utilisateur = self.request.user
            client = Client.objects.get(utilisateur=utilisateur)
            profil = ProfilNutritionnel.objects.get(client=client)
            return profil
        except Client.DoesNotExist:
            raise NotFound('Client non trouvé pour cet utilisateur')
        except ProfilNutritionnel.DoesNotExist:
            raise NotFound('Profil nutritionnel non trouvé')
    
    def get(self, request, *args, **kwargs):
            obj = self.get_object()
            serializer = self.get_serializer(obj)
            return Response(serializer.data)



class SupprimerProfilNutritionnelView(generics.DestroyAPIView):
    """Vue pour supprimer le profil nutritionnel de l'utilisateur courant"""
    serializer_class = ProfilNutritionnelSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        try:
            utilisateur = self.request.user
            client = Client.objects.get(utilisateur=utilisateur)
            profil = ProfilNutritionnel.objects.get(client=client)
            return profil
        except Client.DoesNotExist:
            raise NotFound('Client non trouvé pour cet utilisateur')
        except ProfilNutritionnel.DoesNotExist:
            raise NotFound('Profil nutritionnel non trouvé')
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': 'Profil nutritionnel supprimé avec succès'
        }, status=status.HTTP_200_OK)
    
    def perform_destroy(self, instance):
        instance.delete()



class RecommenderPlatsDirectView(generics.ListAPIView):
    """Vue pour obtenir les plats recommandés basés sur le profil nutritionnel de l'utilisateur"""
    permission_classes = [IsAuthenticated]
    
    # Configuration des limites de recommandation
    MAX_RECOMMENDATIONS = 100
    
    def get_serializer_class(self):
        """Retourne le serializer approprié"""
        return PlatRecommandationSerializer
    
    def get_queryset(self):
        """Retourne les plats recommandés basés sur le profil nutritionnel"""
        try:
            utilisateur = self.request.user
            client = Client.objects.get(utilisateur=utilisateur)
            
            # Récupérer tous les plats disponibles
            plats = Plat.objects.filter(est_disponible=True)[:self.MAX_RECOMMENDATIONS]
            return plats
        except Client.DoesNotExist:
            return Plat.objects.none()
        except Exception as e:
            # Si erreur, retourner les plats disponibles
            return Plat.objects.filter(est_disponible=True)[:self.MAX_RECOMMENDATIONS]
    
    def list(self, request, *args, **kwargs):
        """Retourne les plats recommandés personnalisés pour l'utilisateur avec scores professionnels"""
        try:
            utilisateur = request.user
            client = Client.objects.get(utilisateur=utilisateur)
            profil = client.profil_nutritionnel
            
            # Utiliser la méthode recommander_plats() du profil nutritionnel
            # Cette méthode retourne déjà les plats triés par score
            plats_recommandes = profil.recommander_plats(limite=self.MAX_RECOMMENDATIONS)
            
            # Sérialiser les plats
            serializer = self.get_serializer(plats_recommandes, many=True)
            data = serializer.data
            
            # Calculer le score PROFESSIONNEL pour chaque plat
            for i, plat_data in enumerate(data):
                try:
                    plat = Plat.objects.get(id_plat=plat_data['id_plat'])
                    # Utiliser la nouvelle méthode professionnelle
                    score = Plat.calculer_score_professionnel(plat, profil)
                    plat_data['score'] = score
                except Plat.DoesNotExist:
                    plat_data['score'] = 0.0
            
            # Trier par score décroissant
            data = sorted(data, key=lambda x: x['score'], reverse=True)
            
            return Response(data, status=status.HTTP_200_OK)
        
        except ProfilNutritionnel.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)
        except Client.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Erreur dans recommander_plats: {str(e)}")
            import traceback
            traceback.print_exc()
            # Si erreur, retourner les plats disponibles avec score par défaut
            plats = Plat.objects.filter(est_disponible=True)[:self.MAX_RECOMMENDATIONS]
            serializer = self.get_serializer(plats, many=True)
            data = serializer.data
            
            # Ajouter un score par défaut
            for plat_data in data:
                plat_data['score'] = 0.0
            
            return Response(data, status=status.HTTP_200_OK)

