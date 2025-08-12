#!/bin/bash

gunicorn --worker-class eventlet -w 1 app:app &
FLASK_PID=$!

echo "Waiting for Flask to start..."
until curl -s http://localhost:8000 > /dev/null; do
  sleep 1
done

# Start workers
celery -A app.celery worker --loglevel=info &
celery -A app.celery beat --loglevel=info &

wait $FLASK_PID
