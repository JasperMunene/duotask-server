import logging
from celery_app import celery
from flask import current_app
from workers.instant_recomendation import recommend_best_user_for_task

logger = logging.getLogger(__name__)

BATCH_KEY = "duotasks:recommendation:batch"

@celery.task(bind=True, name="workers.process_batch_recommendation")
def process_batch_recommendation(self):
    try:
        with current_app.app_context():
            redis_client = current_app.redis

        if not redis_client:
            logger.error("Redis client not available. Cannot process batch recommendation.")
            return

        task_ids_raw = redis_client.smembers(BATCH_KEY)
        if not task_ids_raw:
            logger.info("No tasks in batch queue.")
            return

        task_ids = []
        for tid in task_ids_raw:
            try:
                task_ids.append(int(tid.decode()))
            except Exception as e:
                logger.warning(f"Could not decode task_id {tid}: {e}")

        if not task_ids:
            logger.warning("All task_ids were invalid or failed to decode.")
            return

        logger.info(f"Processing {len(task_ids)} task IDs from batch: {task_ids}")

        # Clear the batch queue
        redis_client.delete(BATCH_KEY)

        # Trigger individual recommendations
        for task_id in task_ids:
            logger.info(f"Queuing recommendation for task_id: {task_id}")
            recommend_best_user_for_task.delay(task_id)

    except Exception as e:
        logger.exception(f"Unexpected error while processing batch recommendation: {e}")
