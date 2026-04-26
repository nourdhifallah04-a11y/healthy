# Endpoint à ajouter à la fin de myapp/views.py

class RecommenderN8nWebhookView(generics.GenericAPIView):
    """
    Vue pour appeler le webhook n8n et obtenir les recommandations nutritionnelles.
    
    POST /api/profil-nutritionnel/recommander-n8n/
    Body: {
        "profil_id": 1  (optionnel, utilisera le profil de l'utilisateur courant sinon)
    }
    
    Webhook n8n: http://localhost:5678/webhook/reco-nutrition
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """
        Appelle le webhook n8n avec les données du profil nutritionnel
        et retourne les recommandations
        """
        try:
            # Récupérer le profil nutritionnel
            profil_id = request.data.get('profil_id')
            
            if profil_id:
                try:
                    profil = ProfilNutritionnel.objects.get(id=profil_id)
                except ProfilNutritionnel.DoesNotExist:
                    return Response({
                        'success': False,
                        'error': 'Profil nutritionnel non trouvé'
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                # Utiliser le profil de l'utilisateur courant
                try:
                    utilisateur = request.user
                    client = Client.objects.get(utilisateur=utilisateur)
                    profil = ProfilNutritionnel.objects.get(client=client)
                except (Client.DoesNotExist, ProfilNutritionnel.DoesNotExist):
                    return Response({
                        'success': False,
                        'error': 'Profil nutritionnel non trouvé pour cet utilisateur'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Préparer le payload pour n8n
            payload = {
                'profil': {
                    'age': profil.age,
                    'poids': float(profil.poids),
                    'taille': float(profil.taille),
                    'sexe': profil.sexe,
                    'objectif': profil.objectif,
                    'allergies': profil.allergies or '',
                    'restrictions_alimentaires': profil.restrictions_alimentaires or '',
                    'niveau_activite': profil.niveau_activite,
                    # Ajouter les calculs nutritionnels
                    'imc': profil.calculer_imc(),
                    'bmr': profil.calculer_bmr(),
                    'calories_cibles': profil.besoins_caloriques_journaliers(),
                    'categorie_imc': profil.determiner_categorie_imc()
                },
                'plats_filtrés': [],
                'menus_filtrés': []
            }
            
            # Récupérer les plats disponibles
            plats = Plat.objects.filter(est_disponible=True)
            for plat in plats:
                payload['plats_filtrés'].append({
                    'id': plat.id_plat,
                    'nom': plat.nom,
                    'description': plat.description,
                    'calories': plat.calorie,
                    'proteines': plat.proteine,
                    'glucides': plat.glucides,
                    'lipides': plat.lipides,
                    'fibres': plat.fibres,
                    'prix': float(plat.prix)
                })
            
            # Récupérer les menus actifs
            menus = Menu.objects.filter(est_actif=True)
            for menu in menus:
                valeurs = menu.calculer_valeur_nutritionnelle_totale()
                payload['menus_filtrés'].append({
                    'id': menu.id_menu,
                    'nom': menu.nom,
                    'description': menu.description,
                    'calories': valeurs.get('calories', 0),
                    'proteines': valeurs.get('proteines', 0),
                    'glucides': valeurs.get('glucides', 0),
                    'lipides': valeurs.get('lipides', 0),
                    'prix': float(valeurs.get('prix', 0))
                })
            
            # Appeler le webhook n8n
            webhook_url = 'http://localhost:5678/webhook/reco-nutrition'
            
            logger.info(f"Appel du webhook n8n: {webhook_url}")
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            
            try:
                response = requests.post(
                    webhook_url,
                    json=payload,
                    timeout=30  # Timeout de 30 secondes
                )
                
                logger.info(f"Réponse n8n (status {response.status_code}): {response.text}")
                
                if response.status_code == 200:
                    try:
                        recommendations = response.json()
                    except json.JSONDecodeError:
                        recommendations = {'raw_response': response.text}
                    
                    return Response({
                        'success': True,
                        'message': 'Recommandations obtenues avec succès',
                        'profil': payload['profil'],
                        'recommendations': recommendations
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'success': False,
                        'error': f'Erreur du webhook n8n: {response.status_code}',
                        'details': response.text
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Erreur de connexion au webhook n8n: {str(e)}")
                return Response({
                    'success': False,
                    'error': f'Impossible de se connecter au webhook n8n: {str(e)}',
                    'webhook_url': webhook_url
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            except requests.exceptions.Timeout as e:
                logger.error(f"Timeout du webhook n8n: {str(e)}")
                return Response({
                    'success': False,
                    'error': f'Timeout du webhook n8n: {str(e)}'
                }, status=status.HTTP_504_GATEWAY_TIMEOUT)
            
            except Exception as e:
                logger.error(f"Erreur lors de l'appel au webhook n8n: {str(e)}")
                return Response({
                    'success': False,
                    'error': f'Erreur lors de l\'appel au webhook: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            logger.error(f"Erreur générale dans RecommenderN8nWebhookView: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
