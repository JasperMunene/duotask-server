from celery import Celery
import os

# Create Celery instance
celery = Celery('tasks')

# Basic Celery configuration
celery.conf.update(
    broker_url=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    result_backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    imports=['workers']
)

def init_celery(app):
    """Initialize Celery with existing Flask app"""
    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    celery.flask_app = app  # Store app reference for tasks
    return celery

# start celery worker with:
# celery -A app.celery worker --loglevel=info