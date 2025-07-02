from flask import current_app
from models import db
from models.task import Task
import requests
from models.category import Category
from models.task_image import TaskImage
from sqlalchemy import func, desc
# import google.generativeai as genai  # ❌ Commented out
import logging
import os
import time
from datetime import datetime, timedelta
from celery.schedules import crontab

logger = logging.getLogger(__name__)

# Configuration
BATCH_SIZE = 500
CHUNK_SIZE = 50
RETENTION_DAYS = 30
MAX_RETRIES = 3
RETRY_DELAY = 300

from celery_app import celery


def categorize_task_manually(task_title, task_description, category_names):
    api_key = os.getenv('GEMINI_API_KEY')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    prompt = f"""
    You are a task categorization assistant for a gig marketplace.

    Objective:
    1. Analyze the following task: "{task_title}" - {task_description}"
    2. Choose the MOST SUITABLE category from this list: {', '.join(category_names) or 'None'}
    3. If no category fits well, you are allowed to create a NEW category that is highly relevant.
    4. Do NOT return "Uncategorized".
    5. Pick a category that best describes the NATURE of the work or the type of help requested.

    Output Format:
    Return ONLY the category name — no extra explanation.

    Examples:
    - Task: "Fix broken sink" → "Plumbing"
    - Task: "Design a company logo" → "Graphic Design"
    - Task: "Wait in line at government office" → "Errands"
    - Task: "Help move a couch upstairs" → "Moving Help"
    
    or any relevant categoty that you think, the app is open to new categories.
    Task to Categorize:
    "{task_title}" - {task_description}"

    Output:
    """


    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 20
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        category = data['candidates'][0]['content']['parts'][0]['text'].strip().title()[:50].strip(' .')
        return category or "Uncategorized"
    else:
        logger.error(f"Gemini API Error: {response.status_code} - {response.text}")
        return "Uncategorized"


@celery.task(bind=True, max_retries=3, default_retry_delay=30)
def categorize_task(self, task_id):
    """Background task for AI categorization"""
    try:
        task = Task.query.options(db.joinedload(Task.categories)).get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return

        existing_categories = Category.query.with_entities(Category.name).all()
        category_names = [c[0] for c in existing_categories]

        # Use manual Gemini API call instead of genai SDK
        category_name = categorize_task_manually(task.title, task.description, category_names)

        category = next(
            (c for c in Category.query.all() if c.name.lower() == category_name.lower()),
            None
        )

        if not category:
            category = Category(name=category_name)
            db.session.add(category)
            db.session.flush()

        if category not in task.categories:
            task.categories.append(category)

            uncategorized = next(
                (c for c in task.categories if c.name.lower() == "uncategorized"),
                None
            )
            if uncategorized:
                task.categories.remove(uncategorized)

            db.session.commit()
            logger.info(f"Successfully categorized task {task_id} as {category_name}")
        else:
            logger.info(f"Task {task_id} already has category {category_name}")

        return category_name

    except Exception as e:
        logger.error(f"Failed to categorize task {task_id}: {str(e)}")
        self.retry(exc=e)

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=23, minute=0),
        permanent_deletion_worker.s(),
        name='scheduled-permanent-deletion',
        expires=3600
    )

@celery.task(bind=True, acks_late=True, max_retries=MAX_RETRIES, queue='default')
def permanent_deletion_worker(self):
    """Enterprise-grade deletion worker with advanced features"""
    logger.info("Permanent deletion worker has started execution.")
    try:
        redis = current_app.redis
        start_time = time.monotonic()
        total_deleted = 0
        failure_count = 0

        cutoff_date = datetime.utcnow() - timedelta(days=RETENTION_DAYS)
        logger.info(f"Starting permanent deletion process for tasks deleted before {cutoff_date}")

        query = Task.query.filter(
            Task.is_deleted.is_(True),
            Task.deleted_at <= cutoff_date
        ).order_by(desc(Task.deleted_at))

        last_id = None
        while True:
            batch = query
            if last_id:
                batch = batch.filter(Task.id < last_id)

            tasks = batch.limit(BATCH_SIZE).all()
            if not tasks:
                break

            for chunk in chunked(tasks, CHUNK_SIZE):
                try:
                    chunk_deleted = process_deletion_chunk(chunk)
                    total_deleted += chunk_deleted
                except Exception as chunk_error:
                    logger.error(f"Chunk processing failed: {chunk_error}")
                    failure_count += len(chunk)
                    continue

            last_id = tasks[-1].id
            db.session.expunge_all()  # Prevent memory bloat

        duration = time.monotonic() - start_time
        logger.info(
            f"Deletion completed. Total: {total_deleted}, "
            f"Failures: {failure_count}, Duration: {duration:.2f}s"
        )

        # Update metrics in Redis
        redis.hincrby('worker_metrics', 'tasks_deleted', total_deleted)
        redis.hincrby('worker_metrics', 'deletion_failures', failure_count)

        logger.info(f"'deleted': {total_deleted}, 'failures': {failure_count}, 'duration': {duration}")
        return {'deleted': total_deleted, 'failures': failure_count, 'duration': duration}
        
    except Exception as e:
        logger.critical(f"Critical worker failure: {str(e)}")
        self.retry(countdown=RETRY_DELAY ** (self.request.retries + 1), exc=e)

def process_deletion_chunk(chunk):
    """Process a chunk of tasks with individual transactions"""
    deleted_count = 0
    for task in chunk:
        try:
            with db.session.begin_nested():  # Nested transaction per task
                delete_task_assets(task)
                db.session.delete(task)
                invalidate_task_caches(task)
                deleted_count += 1
        except Exception as e:
            logger.error(f"Failed to delete task {task.id}: {str(e)}")
            db.session.rollback()
            continue

    db.session.commit()  # Commit all successful deletions
    return deleted_count

def delete_task_assets(task):
    """Efficiently delete related entities using bulk operations"""
    # Delete location if exists
    if hasattr(task, 'location') and task.location:
        db.session.delete(task.location)

    # Bulk delete images
    TaskImage.query.filter_by(task_id=task.id).delete()

    # Clear category associations (do not delete the category itself)
    task.categories = []

def invalidate_task_caches(task):
    """Efficient cache invalidation with pipelining"""
    redis = current_app.redis  # Retrieve Redis from app context
    pipe = redis.pipeline()

    # Invalidate task-specific cache
    pipe.delete(f"task_{task.id}")

    # Invalidate user-related task caches
    keys = redis.keys(f"user_{task.user_id}_tasks*")
    if keys:
        pipe.delete(*keys)
    pipe.delete("recent_tasks", "featured_tasks")

    # Mark for delayed list invalidation
    pipe.sadd("pending_cache_invalidations", f"tasks_{task.user_id}")

    pipe.execute()

def chunked(iterable, size):
    """Efficient chunking generator"""
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]
