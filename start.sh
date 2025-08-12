#!/bin/bash
# Start Celery worker in background
celery -A app.celery worker --loglevel=info &

# Start Celery beat in background
celery -A app.celery beat --loglevel=info &

# Start Flask web server
gunicorn --worker-class eventlet -w 1 app:app
