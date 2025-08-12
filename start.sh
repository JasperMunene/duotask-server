#!/bin/bash

# Start Flask web server in background
gunicorn --worker-class eventlet -w 1 app:app &
FLASK_PID=$!

# Wait for Flask to start (adjust port as needed)
echo "Waiting for Flask to start..."
while ! nc -z localhost 8000; do
  sleep 1
done

# Start Celery worker
celery -A app.celery worker --loglevel=info &

# Start Celery beat
celery -A app.celery beat --loglevel=info &

# Wait for Flask to exit
wait $FLASK_PID
