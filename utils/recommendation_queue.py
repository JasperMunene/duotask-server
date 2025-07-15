from flask import current_app
from logger import logging

logger = logging.getLogger(__name__)
BATCH_KEY = "duotasks:recommendation:batch"

def add_task_to_batch(task_id):
    try:
        with current_app.app_context():
            # Ensure the Redis client is available in the app context
            redis_client = current_app.redis
            if not redis_client:
                raise RuntimeError("Redis client not available.")
           
            redis_client.sadd(BATCH_KEY, task_id)
            logger.info(f"Task {task_id} added to batch queue.")
        
    except Exception as exc:
        logger.error(f"Error in recommending users for task {task_id}: {exc}")
        raise exc
