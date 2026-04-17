# Healthy Project Structure

## Directory Organization

```
healthy/
├── core/                          # Project-wide configuration
│   ├── __init__.py
│   ├── settings.py               # Django settings (moved from myapp/)
│   ├── urls.py                   # Root URL configuration
│   ├── asgi.py                   # ASGI configuration
│   └── wsgi.py                   # WSGI configuration
│
├── apps/                          # Django applications
│   ├── __init__.py
│   ├── users/                    # User authentication & profiles
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── apps.py
│   │
│   ├── plats/                    # Dishes/menu items
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── apps.py
│   │
│   ├── commande/                 # Orders
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── apps.py
│   │
│   ├── contact/                  # Contact management
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── apps.py
│   │
│   └── specialdiet/              # Special diet management
│       ├── __init__.py
│       ├── models.py
│       ├── views.py
│       ├── serializers.py
│       ├── forms.py
│       ├── urls.py
│       ├── admin.py
│       └── apps.py
│
├── utils/                         # Shared utilities
│   ├── __init__.py
│   ├── helpers.py                # Common helper functions
│   ├── validators.py             # Custom validators
│   ├── decorators.py             # Custom decorators
│   └── constants.py              # Project constants
│
├── tests/                         # Centralized test suite
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration
│   ├── test_users/
│   ├── test_plats/
│   ├── test_commande/
│   ├── test_contact/
│   └── test_api/
│
├── docs/                          # Documentation
│   ├── SETUP.md
│   ├── API.md
│   ├── FEATURES.md
│   ├── TROUBLESHOOTING.md
│   └── reports/                  # Old reports and summaries
│
├── static/                        # Static assets (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/                     # HTML templates
│   ├── base.html
│   ├── users/
│   ├── plats/
│   ├── commande/
│   ├── contact/
│   └── specialdiet/
│
├── media/                         # User uploaded media
│   └── plats/
│
├── manage.py                      # Django management
├── requirements.txt               # Python dependencies
├── Pipfile / Pipfile.lock         # Pipenv dependencies
├── .env.example                   # Environment template
├── README.md                      # Project overview
└── STRUCTURE.md                   # This file
```

## Architecture Principles

### 1. **Separation of Concerns**
- Each app handles a specific domain (users, plats, commande, etc.)
- Models contain business logic
- Views handle HTTP requests
- Serializers handle API serialization
- Forms handle form validation

### 2. **Configuration Management**
- Core settings in `core/settings.py`
- Environment-specific config via `.env` files
- Clear development/production separation

### 3. **Utilities**
- Reusable functions in `utils/`
- No circular dependencies
- Clear naming conventions

### 4. **Testing**
- Tests organized by app
- Pytest + Django test suite
- Fixtures in `conftest.py`

### 5. **Documentation**
- API documentation in `docs/API.md`
- Setup guide in `docs/SETUP.md`
- Troubleshooting in `docs/TROUBLESHOOTING.md`

## File Naming Conventions

- `models.py`: Database models
- `views.py`: View functions/classes
- `serializers.py`: DRF serializers
- `forms.py`: Django forms
- `urls.py`: URL routing
- `admin.py`: Django admin configuration
- `apps.py`: App configuration
- `tests.py` or `test_*.py`: Unit tests

## Import Conventions

```python
# Absolute imports
from apps.users.models import User
from apps.plats.views import PlatListView
from utils.helpers import format_price

# Relative imports (within same app)
from .models import User
from .serializers import UserSerializer
```

## Environment Setup

1. Create `.env` file from `.env.example`
2. Update `INSTALLED_APPS` in `core/settings.py` to include:
   - `apps.users`
   - `apps.plats`
   - `apps.commande`
   - `apps.contact`
   - `apps.specialdiet`

3. Update root `urls.py` in `core/` to include app URLs

## Running Tests

```bash
# Run all tests
pytest

# Run specific app tests
pytest tests/test_users/

# Run with coverage
pytest --cov=apps --cov=utils
```

## Running Development Server

```bash
python manage.py runserver
```

## Production Deployment

Use Gunicorn with the WSGI application:

```bash
gunicorn core.wsgi:application
```
