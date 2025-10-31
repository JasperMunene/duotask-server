from celery import Celery
import os

# Create Celery instance
celery = Celery('tasks')

# Basic Celery configuration
celery.conf.update(
    broker_url=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    result_backend=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    imports=['workers', 'workers.batch_recommendation']
)
celery.conf.beat_schedule = {
    'process-batch-recommendation': {
        'task': 'workers.process_batch_recommendation',
        'schedule': 360.0,  # Run every 60 seconds
        'args': ()
    }
}

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

# start celery worker and batching with:
# celery -A app.celery worker --loglevel=info
# celery -A app.celery beat --loglevel=info