# Setup Guide

## Prerequisites

- Python 3.10+
- pip or pipenv
- Git

## Installation Steps

### 1. Clone the Repository
```bash
git clone <repo-url>
cd healthy
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create Environment File
```bash
cp .env.example .env
# Edit .env with your settings
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Load Initial Data (Optional)
```bash
python manage.py generate_plats
```

### 8. Run Development Server
```bash
python manage.py runserver
```

The application will be available at: `http://localhost:8000`

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov=utils

# Run specific app
pytest tests/test_users/
```

## Project Structure

See `STRUCTURE.md` for the complete project structure documentation.
