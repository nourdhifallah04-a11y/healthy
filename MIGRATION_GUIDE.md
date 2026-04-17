# Django Project Structure Guide

This document provides a comprehensive guide to the reorganized Django project structure.

## New Structure

```
healthy/
├── core/                    # Project configuration
├── apps/                    # Django applications
├── utils/                   # Shared utilities
├── tests/                   # Test suite
├── docs/                    # Documentation
├── templates/              # HTML templates
├── static/                 # Static files
└── media/                  # User uploads
```

## Migration Guide

### Before (Old Structure)
```
myapp/                      # Project config
healthy/                    # Single app
templates/
static/
```

### After (New Structure)
```
core/                       # Project config (from myapp/)
apps/
  ├── users/               # User auth & profiles
  ├── plats/               # Menu items
  ├── commande/            # Orders
  ├── contact/             # Contact management
  └── specialdiet/         # Special diets
utils/                     # Shared utilities
tests/                     # Organized tests
docs/                      # Documentation
```

## Key Changes

### 1. Settings Module
- **Old:** `myapp/settings.py`
- **New:** `core/settings.py`
- Updated `INSTALLED_APPS` to reference new app paths

### 2. Root URLs
- **Old:** `myapp/urls.py`
- **New:** `core/urls.py`
- Includes URLs from all apps under `apps/`

### 3. Application Structure
Each app now follows the standard Django app structure:
```
apps/users/
├── __init__.py
├── models.py              # Data models
├── views.py               # View logic
├── serializers.py         # API serializers
├── forms.py               # Form definitions
├── urls.py                # URL routing
├── admin.py               # Admin interface
├── apps.py                # App configuration
└── tests.py               # App tests
```

### 4. Utilities
Common functions are now centralized:
```
utils/
├── helpers.py             # Helper functions
├── validators.py          # Custom validators
├── decorators.py          # Decorators
└── constants.py           # Constants
```

### 5. Tests
Tests are organized by app:
```
tests/
├── test_users/
├── test_plats/
├── test_commande/
├── test_contact/
├── test_api/
└── conftest.py            # Pytest configuration
```

## Import Changes

### Old Way
```python
from myapp.models import SomeModel
from healthy.models import ProfilNutritionnel
```

### New Way
```python
from apps.users.models import User
from apps.plats.models import Plat
from apps.commande.models import Commande
from utils.helpers import format_price
```

## Environment Variables

Update your `.env` file:

```
DJANGO_SETTINGS_MODULE=core.settings
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

## Running the Application

```bash
# Set environment
export DJANGO_SETTINGS_MODULE=core.settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

## Next Steps

1. **Migrate Existing Code:**
   - Move models from `healthy/` to `apps/users/`
   - Move views to respective app folders
   - Update imports throughout

2. **Update URLs:**
   - Ensure each app has proper `urls.py`
   - Add app URLs to `core/urls.py`

3. **Run Tests:**
   - Update test imports
   - Organize tests by app
   - Run `pytest` to verify

4. **Documentation:**
   - Review `docs/` folder
   - Update API documentation
   - Add contributing guidelines

## Benefits of New Structure

✅ **Separation of Concerns** - Each app handles one domain
✅ **Scalability** - Easy to add new features
✅ **Maintainability** - Clear organization and naming
✅ **Testability** - Tests organized by feature
✅ **Reusability** - Shared utilities in one place
✅ **Best Practices** - Follows Django conventions

## Reference

- [Django Documentation](https://docs.djangoproject.com/)
- [Django Apps Documentation](https://docs.djangoproject.com/en/stable/ref/applications/)
- [Project STRUCTURE.md](./STRUCTURE.md)
