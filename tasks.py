# tasks.py
from app import create_app
from models import db
from models.task import Task
from models.category import Category
from sqlalchemy import func
import google.generativeai as genai
import logging
import os

logger = logging.getLogger(__name__)


def create_celery():
    app = create_app()
    celery = app.celery
    return celery


celery = create_celery()


@celery.task(bind=True, max_retries=3, default_retry_delay=30)
def categorize_task(self, task_id):
    """Background task for AI categorization"""
    app = create_app()
    with app.app_context():
        try:
            task = Task.query.get(task_id)
            if not task:
                logger.error(f"Task {task_id} not found")
                return

            # Get existing categories
            existing_categories = Category.query.with_entities(Category.name).all()
            category_names = [c[0] for c in existing_categories]

            # Generate category using AI
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            model = genai.GenerativeModel('gemini-2.0-flash')

            prompt = f"""Task Categorization Guide:
            1. Analyze this task: "{task.title}" - {task.description}
            2. Existing categories: {', '.join(category_names) or 'None'}
            3. Choose BEST existing category or create new one
            4. Return ONLY the category name
            Examples:
            - "Need plumbing help" → "Plumbing"
            - "Logo design needed" → "Graphic Design"
            Output:"""

            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=20,
                    candidate_count=1
                )
            )

            category_name = response.text.strip().title()[:50].strip(' .') or "Uncategorized"

            # Find or create category
            category = Category.query.filter(
                func.lower(Category.name) == func.lower(category_name)
            ).first()

            if not category:
                category = Category(name=category_name)
                db.session.add(category)
                db.session.commit()

            # Update task with category
            task.categories.append(category)
            db.session.commit()

            logger.info(f"Successfully categorized task {task_id} as {category_name}")
            return category_name

        except Exception as e:
            logger.error(f"Failed to categorize task {task_id}: {str(e)}")
            self.retry(exc=e)