from flask import current_app
from utils.send_notification import Notify
from models import db
from models.user_location import UserLocation
from models.user_info import UserInfo
from models.user import User
from utils.haversine_distance_km import haversine_distance_km
from models.task import Task
from workers.notifications import notify_user
from models.recommended_tasks import RecommendedTasks
import logging
from sqlalchemy.orm import joinedload
from sqlalchemy import and_
import requests
import json
import os
import math
import re

logger = logging.getLogger(__name__)

from celery_app import celery
@celery.task(bind=True, name="workers.instant_recommendation.recommend_best_user_for_task", max_retries=3, default_retry_delay=30)
def recommend_best_user_for_task(self, task_id):
    logger.info(f"Starting recommendation process for task {task_id}")
    try:
        task = Task.query.options(
            joinedload(Task.location),
            joinedload(Task.categories),
            joinedload(Task.images),
            joinedload(Task.user).joinedload(User.user_info)
        ).get(task_id)

        if not task:
            logger.warning(f"No task found with ID {task_id}")
            return
        if task.work_mode != "physical":
            logger.info(f"Task {task_id} is not a physical task. Skipping recommendation.")
            return
        if not task.location:
            logger.info(f"Task {task_id} has no location info. Skipping recommendation.")
            return

        task_lat = float(task.location.latitude)
        task_lon = float(task.location.longitude)
        logger.info(f"Task location: lat={task_lat}, lon={task_lon}")

        LAT_KM = 0.225
        LON_KM = 0.225 / abs(math.cos(math.radians(task_lat)))
        lat_min, lat_max = task_lat - LAT_KM, task_lat + LAT_KM
        lon_min, lon_max = task_lon - LON_KM, task_lon + LON_KM
        logger.debug(f"Bounding box: ({lat_min}, {lat_max}), ({lon_min}, {lon_max})")

        candidates = (
            db.session.query(User, UserInfo, UserLocation)
            .join(UserInfo, User.id == UserInfo.user_id)
            .join(UserLocation, User.id == UserLocation.user_id)
            .filter(
                and_(
                    User.id != task.user_id, 
                    UserLocation.latitude.between(lat_min, lat_max),
                    UserLocation.longitude.between(lon_min, lon_max)
                )
            )
            .all()
        )
        logger.info(f"Found {len(candidates)} candidates within bounding box")

        options = []
        for user, info, loc in candidates:
            distance = haversine_distance_km(task_lat, task_lon, float(loc.latitude), float(loc.longitude))
            if distance > 25:
                logger.debug(f"Skipping user {user.id} - {distance:.2f}km is too far")
                continue
            options.append({
                "user_id": user.id,
                "bio": info.bio or "",
                "tagline": info.tagline or "",
                "distance_km": round(distance, 2)
            })

        logger.info(f"{len(options)} candidates within 25km after distance filtering")

        if not options:
            logger.info(f"No suitable users found within 25km for task {task_id}")
            return

        prompt = build_gemini_prompt(task, options)
        logger.debug(f"Gemini prompt built:\n{prompt}")
        recommended_user_ids = query_gemini_for_best_fit(prompt, options)

        if recommended_user_ids:
            logger.info(f"Gemini recommended user IDs: {recommended_user_ids}")
            db.session.bulk_save_objects([
                RecommendedTasks(task_id=task.id, user_id=user_id)
                for user_id in recommended_user_ids
            ])
            db.session.commit()
            logger.info(f"Saved {len(recommended_user_ids)} recommendations for task {task.id}")

            send_task_recommendation(recommended_user_ids, task)
        else:
            logger.info(f"Gemini returned no recommended user for task {task_id}")

    except Exception as exc:
        logger.error(f"Error in recommending users for task {task_id}: {exc}")
        raise self.retry(exc=exc)

    
def build_gemini_prompt(task, candidates):
    logger.info("Building Gemini prompt...")
    prompt = f"""
    Task:
    Title: {task.title}
    Description: {task.description}
    Location: {task.location.area}, {task.location.city}, {task.location.state}

    Here are candidates with their bios, taglines, and distance in KM:
    """
    for c in candidates:
        prompt += f"\nUser {c['user_id']}:\n  Bio: {c['bio']}\n  Tagline: {c['tagline']}\n  Distance: {c['distance_km']} km\n"

    prompt += "\nChoose the most suitable user based on relevance and proximity. Only return the user_id of the best one."

    logger.info("Gemini prompt complete.")
    return prompt

def query_gemini_for_best_fit(prompt, options):
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    logger.info("Sending request to Gemini for user recommendation...")

    GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    system_instruction = (
        "You are an assistant that selects the best users for a task based on relevance and proximity. "
        "Return a JSON object in this exact format: {\"user_ids\": [123, 456]} with the most suitable user IDs in order. "
        "Do not return anything else besides valid JSON."
    )

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": f"{system_instruction}\n\n{prompt}"}
                ]
            }
        ]
    }

    
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(GEMINI_URL, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        raw_text = data['candidates'][0]['content']['parts'][0]['text']
        logger.debug(f"Raw Gemini response text: {raw_text}")

        # Remove code block markers like ```json ... ```
        clean_text = re.sub(r"```json|```", "", raw_text, flags=re.IGNORECASE).strip()
        logger.debug(f"Cleaned response text: {clean_text}")
        result = json.loads(clean_text)

        user_ids = result.get("user_ids", [])
        matched_ids = [uid for uid in user_ids if any(opt["user_id"] == uid for opt in options)]

        logger.info(f"Matched {len(matched_ids)} user IDs from Gemini output.")
        return matched_ids
    except Exception as e:
        logger.error(f"Gemini request failed: {e}")
        logger.error(f"Gemini raw response: {response.text if 'response' in locals() else 'No response'}")
        return []





def send_task_recommendation(user_ids, task):
    logger.info(f"Sending notifications for task {task.id} to users: {user_ids}")
    try:
        for user_id in user_ids:
            with current_app.app_context():
                message = f"Task '{task.title}' is available for you. Check it out!"
                notify_user.delay(user_id=user_id, message=message, source='task_recommendation')
                logger.info(f"Notification sent to user {user_id} for task {task.id}.")
    except Exception as exc:
        logger.error(f"Failed to send notifications: {exc}")

