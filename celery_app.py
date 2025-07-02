# # celery_app.py
# from celery import Celery
# import os
# from dotenv import load_dotenv
# from flask import current_app

# # Load environment variables
# load_dotenv()

# def make_celery():
#     """Create Celery instance"""
#     celery = Celery(
#         'tasks',
#         broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'), 
#         backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
#     )
    
#     # Configure Celery
#     celery.conf.update(
#         task_serializer='json',
#         accept_content=['json'],
#         result_serializer='json',
#         timezone='UTC',
#         enable_utc=True,
#         imports=['workers.notifications']
#     )
    
#     # Task base class that creates Flask app context
#     # class ContextTask(celery.Task):
#     #     def __call__(self, *args, **kwargs):
#     #         # Import here to avoid circular imports
#     #         with current_app.app_context():
#     #             return self.run(*args, **kwargs)
    
#     # celery.Task = ContextTask
#     return celery

# # Create Celery instance
# celery = make_celery()
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
    imports=['workers.notifications']
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