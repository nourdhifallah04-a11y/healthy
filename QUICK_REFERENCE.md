# Quick Reference Guide

## 📍 You Are Here
Your Django project has been restructured into a professional, scalable architecture.

## 🎯 Start Here

### 1. Understand the Structure
Read: `STRUCTURE.md`

### 2. Prepare Your Environment
```bash
# Create environment file
cp .env.example .env

# Install dependencies  
pip install -r requirements.txt

# Apply migrations
python manage.py migrate
```

### 3. Start Development
```bash
python manage.py runserver
```

---

## 📂 Where Things Are

| What | Where |
|------|-------|
| User authentication | `apps/users/` |
| Menu/Dishes | `apps/plats/` |
| Orders | `apps/commande/` |
| Contact forms | `apps/contact/` |
| Diet management | `apps/specialdiet/` |
| Helper functions | `utils/helpers.py` |
| Validators | `utils/validators.py` |
| Constants | `utils/constants.py` |
| Settings | `core/settings.py` |
| Root URLs | `core/urls.py` |
| Tests | `tests/` |
| Documentation | `docs/` |

---

## 🔄 Common Tasks

### Add a New Model
```bash
# Create in apps/yourapp/models.py
# Then:
python manage.py makemigrations
python manage.py migrate
```

### Create a View
```python
# In apps/yourapp/views.py
from django.views import View
from .models import YourModel

class YourView(View):
    def get(self, request):
        pass
```

### Add URL
```python
# In apps/yourapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('path/', views.your_view, name='name'),
]

# Then add to core/urls.py:
# path('yourapp/', include('apps.yourapp.urls')),
```

### Run Tests
```bash
pytest                      # All tests
pytest tests/test_users/   # Specific app
pytest --cov=apps         # With coverage
```

### Add Dependency
```bash
pip install package_name
pip freeze > requirements.txt
```

---

## 📚 Documentation Map

```
docs/
├── SETUP.md              ← Installation guide
├── API.md                ← API endpoints
├── FEATURES.md           ← Features list
└── TROUBLESHOOTING.md    ← Common issues
```

---

## 🔑 Key Imports

```python
# Users
from apps.users.models import User

# Plats
from apps.plats.models import Plat

# Orders
from apps.commande.models import Commande

# Utilities
from utils.helpers import format_price
from utils.validators import validate_positive_number
from utils.constants import DEFAULT_PAGE_SIZE

# Settings
from django.conf import settings
```

---

## ⚙️ Environment Variables

```bash
DJANGO_SETTINGS_MODULE=core.settings
DJANGO_SECRET_KEY=your-key
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## 🚨 If Something Goes Wrong

1. **Database error?** → `python manage.py migrate`
2. **Import error?** → `pip install -r requirements.txt`
3. **Static files?** → `python manage.py collectstatic`
4. **Settings error?** → Check `core/settings.py`

See `docs/TROUBLESHOOTING.md` for more help.

---

## 📞 Getting Help

- 📖 Read `STRUCTURE.md` for structure details
- 🔄 Read `MIGRATION_GUIDE.md` to migrate code
- 🆘 Check `docs/TROUBLESHOOTING.md` for issues
- 📝 Check `docs/SETUP.md` for setup help

---

## ✨ That's It!

Your project is now properly structured and ready for development.

**Start building!** 🚀
