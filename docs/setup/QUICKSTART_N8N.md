# ⚡ Démarrage Rapide - Webhook N8N

## 📦 Installation rapide (2 minutes)

### 1. Installer les dépendances
```bash
cd c:\Users\achra\Desktop\wockspace\Nouveau\ dossier\healthy
pip install requests>=2.28.0
```

### 2. Démarrer Django
```bash
python manage.py runserver
```

L'endpoint est maintenant disponible à:
```
POST http://localhost:8000/profilNutritionnel/api/profil-nutritionnel/recommander-n8n/
```

## 🧪 Test rapide (1 minute)

### Option 1: Test sans authentification
```bash
python test_n8n_webhook.py --test-n8n
```

Cela teste uniquement si N8N est accessible.

### Option 2: Test complet avec curl
```bash
# D'abord obtenir un token
curl -X POST http://localhost:8000/api/token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"email": "votre@email.com", "password": "votre_password"}'

# Puis tester l'endpoint (remplacez TOKEN par le token reçu)
curl -X POST http://localhost:8000/profilNutritionnel/api/profil-nutritionnel/recommander-n8n/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## 📝 Fichiers importants

1. **myapp/views.py** - Classe `RecommenderN8nWebhookView` ajoutée (ligne ~1246)
2. **myapp/urls.py** - Route créée
3. **requirements.txt** - Dépendances mises à jour
4. **N8N_WEBHOOK_DOCUMENTATION.md** - Documentation complète
5. **N8N_PAYLOAD_EXAMPLES.md** - Exemples de payloads
6. **test_n8n_webhook.py** - Script de test
7. **N8N_IMPLEMENTATION_COMPLETE.md** - Résumé complet

## 🔗 Endpoint créé

```
POST /profilNutritionnel/api/profil-nutritionnel/recommander-n8n/
```

**Requis:** Token JWT  
**Optionnel:** `profil_id` dans le body JSON

**Réponse:**
```json
{
  "success": true,
  "profil": {...},
  "recommendations": {...}
}
```

## 🎯 Flux complet

1. **Client** → POST `/profilNutritionnel/api/profil-nutritionnel/recommander-n8n/`
2. **Django** → Récupère le profil nutritionnel
3. **Django** → Prépare le payload avec plats et menus
4. **Django** → Appelle le webhook N8N
5. **N8N** → Analyse et score les plats/menus
6. **N8N** → Retourne les recommandations
7. **Django** → Envoie les résultats au client

## 🛠️ Où configurer N8N?

L'URL du webhook est:
```
http://localhost:5678/webhook/reco-nutrition
```

Si vous utilisez un port différent, modifiez cette ligne dans `views.py`:
```python
webhook_url = 'http://localhost:5678/webhook/reco-nutrition'
```

## 📊 Exemple de payload reçu par N8N

```json
{
  "profil": {
    "age": 28,
    "poids": 75.0,
    "taille": 175.0,
    "objectif": "prise_muscle",
    "imc": 24.49,
    "bmr": 1755.53,
    "calories_cibles": 2437.77,
    ...
  },
  "plats_filtrés": [
    {
      "id": 1,
      "nom": "Poulet rôti",
      "calories": 450.0,
      "proteines": 45.0,
      ...
    }
  ],
  "menus_filtrés": [...]
}
```

## ✅ Checklist déploiement

- [ ] `requirements.txt` mis à jour
- [ ] `pip install -r requirements.txt` exécuté
- [ ] Django redémarré
- [ ] `python manage.py check` sans erreurs
- [ ] N8N démarré et accessible
- [ ] Webhook N8N configuré
- [ ] Test avec `test_n8n_webhook.py` réussi
- [ ] Frontend intégré (optionnel)

## 🚀 Commandes importantes

```bash
# Installer les dépendances
pip install -r requirements.txt

# Redémarrer Django
python manage.py runserver

# Vérifier les erreurs Django
python manage.py check

# Tester N8N
python test_n8n_webhook.py --test-n8n

# Tester l'endpoint complet
python test_n8n_webhook.py --token YOUR_TOKEN

# Voir les logs
# Vérifiez la console où Django est lancé
```

## 🐛 Si ça ne marche pas

### Erreur 1: "ModuleNotFoundError: No module named 'requests'"
```bash
pip install requests
```

### Erreur 2: "Impossible de se connecter au webhook n8n"
```bash
# Vérifiez que N8N est lancé
# Testez la connectivité
curl http://localhost:5678/webhook/reco-nutrition
```

### Erreur 3: "Profil nutritionnel non trouvé"
→ L'utilisateur doit créer un profil nutritionnel d'abord  
→ Testez avec `/profilNutritionnel/api/profil-nutritionnel/obtenir/`

### Erreur 4: "401 Unauthorized"
→ Token JWT invalide ou expiré  
→ Obtenez un nouveau token

## 📚 Documentation

Pour plus de détails, consultez:
- **N8N_WEBHOOK_DOCUMENTATION.md** - Guide complet
- **N8N_PAYLOAD_EXAMPLES.md** - Exemples détaillés
- **N8N_IMPLEMENTATION_COMPLETE.md** - Résumé technique

## 💡 Astuces

1. **Logs:** Tous les appels à N8N sont loggés dans la console Django
2. **Debug:** Lancez `python manage.py shell` pour tester manuellement
3. **Tests:** Utilisez le script `test_n8n_webhook.py` pour valider
4. **Production:** Configurez les variables d'environnement pour l'URL N8N

## 🎉 C'est terminé!

L'endpoint est maintenant prêt à être utilisé. Lancez:

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Redémarrer Django  
python manage.py runserver

# 3. Tester
python test_n8n_webhook.py --test-n8n

# ✅ Vous êtes prêt!
```

---

**Questions?** Consultez la documentation dans les fichiers `.md`  
**Besoin d'aide?** Vérifiez les logs Django et N8N
