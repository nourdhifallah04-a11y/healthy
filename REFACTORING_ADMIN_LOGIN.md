# Refactoring - Formulaire de Connexion Admin

## Vue d'ensemble
Le formulaire de connexion administrateur a été refactorisé pour utiliser une approche plus robuste et sécurisée en récupérant l'administrateur directement depuis la base de données.

---

## Améliorations apportées

### 1. **Nouvelle Classe Form** (`AdminLoginForm`)

**Fichier:** `myapp/forms.py`

```python
class AdminLoginForm(forms.ModelForm):
    """Formulaire de connexion pour les administrateurs"""
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre email',
            'autocomplete': 'email'
        })
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre mot de passe',
            'autocomplete': 'current-password'
        })
    )
```

**Avantages:**
- Utilisation de l'email comme identifiant (cohérent avec le modèle `Utilisateur`)
- Validation automatique du format email
- Attributs HTML5 pour meilleure UX
- Compatibilité avec les gestionnaires de mots de passe

---

### 2. **Fonction Refactorisée** (`login_admin`)

**Fichier:** `myapp/views.py`

**Avant:**
```python
def login_admin(request):
    if request.method == "POST":
        username = request.POST.get('identifiant')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        # ... logique minimale
```

**Après:**
```python
@require_http_methods(["GET", "POST"])
def login_admin(request):
    """
    Formulaire de connexion pour les administrateurs.
    Récupère l'administrateur à partir de l'email et de la base de données.
    """
    if request.method == "POST":
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            
            try:
                # 1. Récupérer l'utilisateur par email depuis la base de données
                utilisateur = Utilisateur.objects.get(email=email)
                
                # 2. Vérifier que le mot de passe est correct
                if utilisateur.check_password(password):
                    # 3. Vérifier si cet utilisateur est un administrateur
                    if hasattr(utilisateur, 'administrateur'):
                        administrateur = Utilisateur.objects.get(email=email)
                        login(request, administrateur)
                        messages.success(request, f"Bienvenue {administrateur.prenom} {administrateur.nom}!")
                        return redirect('dashboard_admin')
                    else:
                        messages.error(request, "Vous n'avez pas les droits d'accès administrateur.")
                        form.add_error(None, "Accès refusé : vous n'êtes pas un administrateur.")
                else:
                    messages.error(request, "Mot de passe incorrect.")
                    form.add_error('password', "Le mot de passe est incorrect.")
                    
            except Utilisateur.DoesNotExist:
                messages.error(request, "Aucun utilisateur trouvé avec cet email.")
                form.add_error('email', "Cet email n'existe pas dans la base de données.")
            except Exception as e:
                messages.error(request, f"Une erreur est survenue : {str(e)}")
                form.add_error(None, f"Erreur lors de la connexion : {str(e)}")
    else:
        form = AdminLoginForm()
    
    context = {
        'form': form,
        'page_title': 'Connexion Administrateur'
    }
    return render(request, 'administrateur/login_admin.html', context)
```

**Améliorations:**
- ✅ Récupération directe de l'utilisateur par email depuis la BD
- ✅ Validation sécurisée du mot de passe avec `check_password()`
- ✅ Vérification d'une relation `administrateur` existante
- ✅ Gestion complète des erreurs avec messages utilisateur
- ✅ Utilisation de `@require_http_methods` pour sécurité HTTP
- ✅ Messages de feedback détaillés
- ✅ Gestion des exceptions spécifiques
- ✅ Contexte enrichi pour le template

---

### 3. **Processus de Vérification (3 étapes)**

```
1. Récupérer l'utilisateur par email
   ↓
2. Vérifier le mot de passe
   ↓
3. Vérifier que l'utilisateur est un administrateur (relation OneToOne)
   ↓
4. Connecter et rediriger
```

**Avantage:** Séparation claire des responsabilités et des points de contrôle.

---

### 4. **Gestion des Erreurs**

| Erreur | Message | Réponse |
|--------|---------|---------|
| Email non trouvé | "Cet email n'existe pas dans la base de données." | Affiche le formulaire avec erreur |
| Mot de passe incorrect | "Le mot de passe est incorrect." | Affiche le formulaire avec erreur |
| Pas administrateur | "Accès refusé : vous n'êtes pas un administrateur." | Refuse la connexion |
| Autres erreurs | Message d'exception générique | Affiche le formulaire avec erreur |

---

### 5. **Template Dédié** (`login_admin.html`)

**Créé à:** `templates/administrateur/login_admin.html`

**Caractéristiques:**
- Design moderne et professionnel
- Gradient couleur signature (violet)
- Affichage des messages de succès/erreur
- Validation côté client et serveur
- Responsive design
- Accessibilité HTML5 améliorée

---

## Modifications d'Imports

**Fichier:** `myapp/views.py`

```python
# Ajouts:
from .models import Administrateur, Utilisateur  # ← Modèles supplémentaires
from .forms import AdminLoginForm                 # ← Nouveau formulaire
from django.contrib import messages              # ← Messages flash
from django.views.decorators.http import require_http_methods  # ← Décorateur sécurité
```

---

## Utilisation

### URL Configuration
Assurez-vous que l'URL est configurée dans `urls.py`:

```python
path('admin/login/', login_admin, name='login_admin'),
```

### Vérification de la Structure BD
Pour que cela fonctionne, la structure suivante doit exister:

```
Utilisateur (email unique)
  └─→ Administrateur (OneToOneField)
  └─→ Client (OneToOneField)
```

**Code modèles:**
```python
class Administrateur(models.Model):
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='administrateur')
    # ... autres champs
```

---

## Sécurité

✅ **Mots de passe:** Utilise `check_password()` (hachage Django)
✅ **CSRF Protection:** Token `{% csrf_token %}` dans le formulaire
✅ **Validation:** Validation serveur complète
✅ **SQL Injection:** Protection via ORM Django
✅ **Méthodes HTTP:** Restriction avec `@require_http_methods`
✅ **Messages d'erreur:** Ne révèle pas d'informations sensibles

---

## Tests Recommandés

```python
# Test 1: Email non trouvé
POST /admin/login/ → Email: "inexistant@email.com"
Expected: Erreur "Cet email n'existe pas"

# Test 2: Mot de passe incorrect
POST /admin/login/ → Email: "admin@gmail.com", Password: "wrong"
Expected: Erreur "Le mot de passe est incorrect"

# Test 3: Utilisateur non administrateur
POST /admin/login/ → Email: "client@gmail.com" (client, pas admin)
Expected: Erreur "Vous n'avez pas les droits d'accès administrateur"

# Test 4: Connexion réussie
POST /admin/login/ → Email: "admin@gmail.com", Password: "correct"
Expected: Redirection vers 'dashboard_admin'
```

---

## Changelog

| Version | Date | Modifications |
|---------|------|---------------|
| 2.0 | 2026-04-13 | Refactoring complet - Récupération BD directe, formulaire dédié, meilleure gestion d'erreurs |
| 1.0 | Ancien | Logique minimale sans validation |

---

## Fichiers Modifiés

- ✏️ `myapp/forms.py` - Ajout `AdminLoginForm`
- ✏️ `myapp/views.py` - Refactoring `login_admin`, ajout imports
- ✨ `templates/administrateur/login_admin.html` - Nouveau template
