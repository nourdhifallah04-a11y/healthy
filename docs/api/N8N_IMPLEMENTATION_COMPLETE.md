# Résumé d'Implémentation - Endpoint Webhook N8N

## ✅ Fichiers modifiés/créés

### 1. **myapp/views.py** (Modifié)
- ✅ Ajout des imports: `requests` et `logging`
- ✅ Nouvelle classe `RecommenderN8nWebhookView`
- Localisation: Fin du fichier, après `UnifiedMenuItemViewSet`

### 2. **myapp/urls.py** (Modifié)
- ✅ Nouvelle route: `path("api/profil-nutritionnel/recommander-n8n/", views.RecommenderN8nWebhookView.as_view(), name="recommander_n8n_webhook")`
- Localisation: Avant la ligne `path("api/", include(router.urls))`

### 3. **requirements.txt** (Modifié)
- ✅ Ajout: `requests>=2.28.0`
- ✅ Ajout: `djangorestframework>=3.14.0`
- ✅ Ajout: `Pillow>=10.0.0`

### 4. **N8N_WEBHOOK_DOCUMENTATION.md** (Créé)
- Documentation complète de l'endpoint
- Exemples d'utilisation
- Gestion des erreurs

### 5. **N8N_PAYLOAD_EXAMPLES.md** (Créé)
- Exemples de payloads échangés
- Format de réponse N8N
- Logique de calcul des scores

### 6. **test_n8n_webhook.py** (Créé)
- Script de test pour valider l'endpoint
- Utile pour déboguer

## 🚀 Déploiement

### Étape 1: Installer les dépendances
```bash
pip install -r requirements.txt
```

### Étape 2: Redémarrer Django
```bash
python manage.py runserver
```

### Étape 3: Vérifier que tout fonctionne
```bash
python test_n8n_webhook.py --test-n8n
```

## 📋 Endpoint créé

**POST** `/profilNutritionnel/api/profil-nutritionnel/recommander-n8n/`

### Paramètres
- `profil_id` (optionnel): ID du profil (sinon utilise le profil de l'utilisateur courant)

### Authentification
- Requiert un token JWT ou une session Django
- Header: `Authorization: Bearer <TOKEN>`

### Réponse réussie (200)
```json
{
  "success": true,
  "message": "Recommandations obtenues avec succès",
  "profil": { ... },
  "recommendations": { ... }
}
```

## 🔗 Webhook N8N

L'endpoint appelle:
```
POST http://localhost:5678/webhook/reco-nutrition
```

Assurez-vous que:
1. N8N est démarré et accessible
2. Le webhook est configuré sur la bonne route
3. N8N retourne du JSON valide

## 🧪 Tests recommandés

### Test 1: Connectivité N8N
```bash
python test_n8n_webhook.py --test-n8n
```

### Test 2: Avec authentification
```bash
python test_n8n_webhook.py --token YOUR_TOKEN
```

### Test 3: Avec profil spécifique
```bash
python test_n8n_webhook.py --token YOUR_TOKEN --profil-id 1
```

### Test 4: Curl
```bash
curl -X POST http://localhost:8000/profilNutritionnel/api/profil-nutritionnel/recommander-n8n/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## 📊 Données envoyées à N8N

L'endpoint prépare automatiquement:
- Profil nutritionnel complet (âge, poids, taille, etc.)
- Calculs: IMC, BMR, besoins caloriques
- Liste de tous les plats disponibles
- Liste de tous les menus actifs

Voir `N8N_PAYLOAD_EXAMPLES.md` pour les détails complets.

## 🛡️ Gestion des erreurs

L'endpoint gère:
- ❌ Profil non trouvé → 404
- ❌ N8N indisponible → 503
- ❌ Timeout N8N → 504
- ❌ Erreur N8N → 400
- ❌ Erreur serveur → 500

Tous les erreurs sont loggées.

## 📝 Logs

Cherchez ces messages dans les logs:
```
INFO: Appel du webhook n8n: http://localhost:5678/webhook/reco-nutrition
INFO: Payload: {...}
INFO: Réponse n8n (status 200): {...}
```

## 🔧 Configuration optionnelle

### Changer l'URL N8N
Dans `views.py`, ligne où se trouve:
```python
webhook_url = 'http://localhost:5678/webhook/reco-nutrition'
```

Remplacez par:
```python
webhook_url = 'http://your-n8n-host:5678/webhook/reco-nutrition'
```

Ou utilisez une variable d'environnement:
```python
webhook_url = settings.N8N_WEBHOOK_URL_RECO_NUTRITION
```

### Augmenter le timeout
Cherchez:
```python
timeout=30  # Timeout de 30 secondes
```

Modifiez la valeur au besoin.

## ✨ Cas d'usage

### Use Case 1: Recommandations personnalisées
```bash
# Utilisateur veut des recommandations basées sur son profil
POST /profilNutritionnel/api/profil-nutritionnel/recommander-n8n/
# Le système appelle N8N qui analyse le profil
# N8N retourne les 5 meilleurs plats et 3 meilleurs menus
```

### Use Case 2: Comparaison de plats
```bash
# N8N peut comparer plusieurs profils
# Utile pour des analyses comparatives
```

### Use Case 3: Intégration avec interface web
```javascript
// Frontend appelle l'endpoint
fetch('/profilNutritionnel/api/profil-nutritionnel/recommander-n8n/')
  .then(r => r.json())
  .then(data => afficherRecommandations(data.recommendations))
```

## 🐛 Dépannage

### Erreur: "Impossible de se connecter au webhook n8n"
→ Vérifiez que N8N est démarré et accessible

### Erreur: "Profil nutritionnel non trouvé"
→ L'utilisateur doit créer un profil d'abord

### Erreur: "Timeout"
→ N8N met trop de temps, vérifiez les logs N8N

### Erreur: "401 Unauthorized"
→ Token JWT invalide ou expiré

## 📚 Documentation complète

- [N8N_WEBHOOK_DOCUMENTATION.md](N8N_WEBHOOK_DOCUMENTATION.md) - Guide d'utilisation
- [N8N_PAYLOAD_EXAMPLES.md](N8N_PAYLOAD_EXAMPLES.md) - Exemples de payloads

## 🎯 Prochaines étapes

1. ✅ Implémentation terminée
2. ⏭️ Configurer le workflow N8N
3. ⏭️ Tester l'intégration
4. ⏭️ Intégrer à l'interface frontend (optionnel)
5. ⏭️ Déployer en production

## 📞 Support

Pour toute question:
1. Consultez la documentation dans les `.md`
2. Lancez le script `test_n8n_webhook.py`
3. Vérifiez les logs Django et N8N

---

**Implémentation complétée le:** 2026-04-18  
**Version:** 1.0  
**Statut:** ✅ Prêt pour le déploiement
