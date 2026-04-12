# Healthy Django Project

This repository contains a Django application for managing a user's nutrition profile.

## Stack

- Python 3.12
- Django 6.0.3
- SQLite by default
- Gunicorn for production serving

## Project Structure

- `manage.py`: main Django entrypoint
- `myapp/`: Django project configuration
- `healthy/`: nutrition profile app
- `templates/`: shared base and authentication templates
- `requirements.txt`: pinned Python dependencies

## Features

- Authentication with login/logout
- Admin interface
- Create, view, update, and delete a nutrition profile
- Per-user access protection
- Form validation for profile data
- Initial database migration
- Basic automated tests for the main flow

## Installation

1. Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Apply migrations:

```bash
python manage.py migrate
```

4. Create an admin user if needed:

```bash
python manage.py createsuperuser
```

5. Run the development server:

```bash
python manage.py runserver
```

## Configuration

The project supports environment-based configuration through these variables:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_TIME_ZONE`
- `DJANGO_DB_ENGINE`
- `DJANGO_DB_NAME`
- `DJANGO_DB_USER`
- `DJANGO_DB_PASSWORD`
- `DJANGO_DB_HOST`
- `DJANGO_DB_PORT`

By default, the app uses SQLite with `db.sqlite3`.

## Main URLs

- `/login/`: login page
- `/logout/`: logout
- `/admin/`: Django admin
- `/nutrition/`: nutrition profile area

## Running Tests

```bash
python manage.py test
```

## Production Notes

- Set `DJANGO_DEBUG=0`
- Set a strong `DJANGO_SECRET_KEY`
- Configure `DJANGO_ALLOWED_HOSTS`
- Use Gunicorn to serve the app
- Put a reverse proxy such as Nginx in front of Gunicorn
- Configure static file collection if deploying beyond local development

Example Gunicorn command:

```bash
gunicorn myapp.wsgi:application
```

## Current Status

The project has been repaired and verified with:

- `python manage.py check`
- `python manage.py migrate`
- `python manage.py test`
