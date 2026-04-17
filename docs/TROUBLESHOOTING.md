# Troubleshooting Guide

## Common Issues

### Migration Errors
**Problem:** `No such table: <table_name>`

**Solution:**
```bash
python manage.py migrate
python manage.py migrate --run-syncdb
```

### Import Errors
**Problem:** `ModuleNotFoundError: No module named 'apps'`

**Solution:**
Make sure you're in the project root directory and have installed all dependencies:
```bash
pip install -r requirements.txt
```

### Static Files Not Loading
**Problem:** CSS and JS files return 404

**Solution:**
```bash
python manage.py collectstatic
python manage.py collectstatic --clear --noinput
```

### Database Locked
**Problem:** SQLite database is locked

**Solution:**
1. Stop the development server
2. Delete `db.sqlite3`
3. Run migrations again:
```bash
python manage.py migrate
```

### Port Already in Use
**Problem:** Port 8000 is already in use

**Solution:**
```bash
# Use a different port
python manage.py runserver 8001

# Or kill the process using port 8000
lsof -i :8000
kill -9 <PID>
```

### Settings Module Not Found
**Problem:** `ModuleNotFoundError: No module named 'myapp'`

**Solution:**
Update `DJANGO_SETTINGS_MODULE` environment variable:
```bash
export DJANGO_SETTINGS_MODULE=core.settings
# On Windows
set DJANGO_SETTINGS_MODULE=core.settings
```

## Debug Mode

Enable debug logging:
```python
# In settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

## Getting Help

1. Check the documentation in `docs/`
2. Review error messages carefully
3. Check Django logs
4. Run tests to identify issues
5. Check GitHub issues
