# Architecture Diagram

## Project Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     HEALTHY DJANGO APPLICATION                             │
│                         (Restructured v1.0)                                │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────────┐
                              │   Client Layers  │
                              └────────┬─────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    │                                     │
            ┌───────▼────────┐               ┌───────────▼──────┐
            │   Web Browser  │               │   REST API Client│
            └───────┬────────┘               └────────┬────────┘
                    │                                 │
                    └──────────────────┬──────────────┘
                                       │
              ┌────────────────────────▼────────────────────────┐
              │        CORE URL ROUTING (core/urls.py)         │
              └────────────────────────┬────────────────────────┘
                                       │
        ┌──────────────────┬───────────┼───────────┬──────────────────┐
        │                  │           │           │                  │
   ┌────▼──┐          ┌────▼──┐   ┌────▼──┐   ┌────▼──┐          ┌────▼──┐
   │ USERS │          │ PLATS │   │COMMANDE   │CONTACT│          │SPECIAL│
   │ APP   │          │ APP   │   │ APP      │ APP   │          │ DIET  │
   └────┬──┘          └────┬──┘   └────┬──┘   └────┬──┘          └────┬──┘
        │                  │            │            │                  │
        │  models.py       │  models.py │ models.py  │ models.py        │ models.py
        │  views.py        │  views.py  │ views.py   │ views.py         │ views.py
        │  serializers.py  │  serial.py │ serial.py  │ serial.py        │ serial.py
        │  forms.py        │  forms.py  │ forms.py   │ forms.py         │ forms.py
        │  urls.py         │  urls.py   │ urls.py    │ urls.py          │ urls.py
        │  admin.py        │  admin.py  │ admin.py   │ admin.py         │ admin.py
        └────┬──┘          └────┬──┘    └────┬──┘    └────┬──┘          └────┬──┘
             │                  │            │            │                  │
             └──────────────────┼────────────┼────────────┼──────────────────┘
                                │            │            │
                    ┌───────────▼────────────▼────────────▼────────────┐
                    │      DJANGO ORM & DATABASE LAYER                │
                    │  (Models interact with SQLite/PostgreSQL)        │
                    └────────────────────────┬──────────────────────────┘
                                             │
                    ┌────────────────────────▼──────────────────────────┐
                    │               DATABASE (db.sqlite3)               │
                    │       ┌─────────┬──────────┬────────┬────────┐   │
                    │       │  Users  │  Plats   │Orders  │Contact │  │
                    │       │ Tables  │ Tables   │Tables  │Tables  │  │
                    │       └─────────┴──────────┴────────┴────────┘   │
                    └───────────────────────────────────────────────────┘

                    ┌──────────────────────────────────────────────────┐
                    │         SHARED UTILITIES & HELPERS              │
                    ├──────────────────────────────────────────────────┤
                    │  • utils/helpers.py          (Common functions)  │
                    │  • utils/validators.py       (Data validators)   │
                    │  • utils/decorators.py       (Decorators)        │
                    │  • utils/constants.py        (Constants)         │
                    └──────────────────────────────────────────────────┘

                    ┌──────────────────────────────────────────────────┐
                    │           CONFIGURATION & SETTINGS               │
                    ├──────────────────────────────────────────────────┤
                    │  • core/settings.py          (Django config)     │
                    │  • core/urls.py              (Root URLs)         │
                    │  • core/wsgi.py              (WSGI app)          │
                    │  • core/asgi.py              (ASGI app)          │
                    └──────────────────────────────────────────────────┘

                    ┌──────────────────────────────────────────────────┐
                    │              TEST SUITE                          │
                    ├──────────────────────────────────────────────────┤
                    │  tests/test_users/    ──► User tests            │
                    │  tests/test_plats/    ──► Plats tests           │
                    │  tests/test_commande/ ──► Order tests           │
                    │  tests/test_contact/  ──► Contact tests         │
                    │  tests/test_api/      ──► API tests             │
                    └──────────────────────────────────────────────────┘

                    ┌──────────────────────────────────────────────────┐
                    │            DOCUMENTATION                         │
                    ├──────────────────────────────────────────────────┤
                    │  docs/SETUP.md               (Installation)      │
                    │  docs/API.md                 (API Reference)     │
                    │  docs/FEATURES.md            (Features list)     │
                    │  docs/TROUBLESHOOTING.md     (Help & issues)     │
                    │  STRUCTURE.md                (Full structure)    │
                    │  MIGRATION_GUIDE.md          (Code migration)    │
                    └──────────────────────────────────────────────────┘
```

## Data Flow

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP Request
       │
┌──────▼──────────────────────────┐
│   Django Request Handler         │
│  (URL Router in core/urls.py)    │
└──────┬──────────────────────────┘
       │
┌──────▼──────────────────────────┐
│   App Specific Routing           │
│  (App urls.py)                   │
└──────┬──────────────────────────┘
       │
┌──────▼──────────────────────────┐
│   View Layer                     │
│  (views.py / ViewSets)           │
└──────┬──────────────────────────┘
       │
┌──────▼──────────────────────────┐
│   Serializer Layer               │
│  (Data validation & transform)   │
└──────┬──────────────────────────┘
       │
┌──────▼──────────────────────────┐
│   Model Layer                    │
│  (models.py - Business logic)    │
└──────┬──────────────────────────┘
       │
┌──────▼──────────────────────────┐
│   Database                       │
│  (SQLite / PostgreSQL)           │
└──────────────────────────────────┘

Reverse flow:
Database → Model → Serializer → View → Browser
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────┐
│                    TECHNOLOGY STACK                      │
├─────────────────────────────────────────────────────────┤
│ Backend Framework    │ Django 6.0.3                      │
│ Python Version       │ 3.10+                             │
│ API Framework        │ Django REST Framework             │
│ Database             │ SQLite (dev) / PostgreSQL (prod)  │
│ Web Server           │ Gunicorn (production)             │
│ Package Manager      │ pip / pipenv                       │
│ Testing              │ pytest + Django TestCase          │
│ Code Quality         │ Black, Flake8, isort              │
├─────────────────────────────────────────────────────────┤
│ Development Tools    │ VS Code / PyCharm                 │
│ Version Control      │ Git / GitHub                      │
│ Environments         │ .env configuration                │
└─────────────────────────────────────────────────────────┘
```

## Component Interactions

```
                     ┌──────────────┐
                     │ Client Layer │
                     └──────┬───────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
         ┌────▼─────┐           ┌────────▼──┐
         │   URLs   │           │ Templates │
         │ Routing  │           │   (HTML)  │
         └────┬─────┘           └───────────┘
              │
         ┌────▼──────────────┐
         │   View Layer      │
         │ (Business Logic)  │
         └────┬──────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
┌───▼────┐ ┌─▼────┐ ┌──▼────┐
│ Forms  │ │Models│ │Serialz│
│ Valid  │ │Logic │ │Transform
└────────┘ └──┬───┘ └───────┘
              │
         ┌────▼────────┐
         │ Utilities   │
         │ Helpers     │
         │ Validators  │
         └────┬────────┘
              │
         ┌────▼────────┐
         │  Database   │
         │   (ORM)     │
         └─────────────┘
```

This architecture provides:
- ✅ Clean separation of concerns
- ✅ Modularity and scalability
- ✅ Reusable components
- ✅ Easy testing
- ✅ Maintainability
- ✅ Professional organization
