#!/bin/sh

set -e

if [ "$1" = "web" ]; then
    echo "Starting web server..."
    exec gunicorn \
        --worker-class gevent \
        --workers $GUNICORN_WORKERS \
        --threads $GUNICORN_THREADS \
        --bind $GUNICORN_BIND \
        --access-logfile - \
        --error-logfile - \
        app:app
elif [ "$1" = "celery" ]; then
    echo "Starting Celery worker..."
    exec celery -A tasks.celery worker \
        --loglevel=info \
        --concurrency=4 \
        --queues=ai_tasks,default
elif [ "$1" = "celery-beat" ]; then
    echo "Starting Celery beat..."
    exec celery -A tasks.celery beat \
        --loglevel=info \
        --pidfile=
else
    exec "$@"
fi