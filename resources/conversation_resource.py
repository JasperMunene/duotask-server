# task_resource.py
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app, request
from models.conversation import Conversation
from models.message import Message
from models.user import User
from flask import current_app
from sqlalchemy.orm import joinedload
from models import db
from models.task import Task
from models.task_assignment import TaskAssignment
import datetime

class ConversationResource(Resource):
    @jwt_required()
    def get(self, user_id):
        cache = current_app.cache
        cache_key = f"conversations_user_{user_id}"

        cached_result = cache.get(cache_key)
        # if cached_result:
            # return cached_result

        conversations = Conversation.query.filter(
            (Conversation.task_giver == user_id) | (Conversation.task_doer == user_id)
        ).all()

        result = []
        for convo in conversations:
            recipient_user_id = convo.task_doer if convo.task_giver == user_id else convo.task_giver
            recipient = User.query.get(recipient_user_id)
            # Get the last 5 messages
            last_10_msgs = (
                Message.query
                .filter_by(conversation_id=convo.id)
                .order_by(Message.date_time.desc())  # Use asc() to get messages in ascending order
                .limit(20)
                .all()
            )



            # Format messages
            messages = [
                {
                    "message_id": msg.id,
                    "sender_id": msg.sender_id,
                    "receiver_id": msg.reciever_id,
                    "text": msg.message,
                    "image": msg.image,
                    "time": msg.date_time.isoformat(),
                    "status": msg.status,
                    "sent": int(msg.sender_id) == int(user_id)  # True if sender_id matches user_id, else False
                }
                for msg in last_10_msgs
            ]
            
            # Just get the last message only
            last_msg = (
                Message.query
                .filter_by(conversation_id=convo.id)
                .order_by(Message.date_time.desc())
                .first()
            )

            if not last_msg:
                continue  # skip convos with no messages (just in case)
            last_message_text = (
                "You: photo" if last_msg.sender_id == user_id else "photo"
            ) if not last_msg.message and last_msg.image else (
                f"You: {last_msg.message}" if last_msg.sender_id == user_id else last_msg.message
            )

            unread = last_msg.reciever_id == user_id and last_msg.status != "read"

            task = Task.query.get(convo.task_id)
            assignment = TaskAssignment.query.filter_by(task_id=convo.task_id).first()

            task_info = {
                "title": task.title if task else None,
                "description": task.description if task else None,
                "status": task.status if task else None
            } if task else {}

            assignment_info = {
                "agreed_price": float(assignment.agreed_price) if assignment else None,
                "status": assignment.status if assignment else None
            } if assignment else {}

            result.append({
                "id": convo.id,
                "archived": convo.archived,
                "task_giver": convo.task_giver,
                "task_doer": convo.task_doer,
                "recipient": {
                    "user_id": recipient.id,
                    "name": recipient.name,
                    "avator": recipient.image,
                    "status": recipient.status,
                    "last_seen": recipient.last_seen.isoformat()
                },
                "messages": messages,
                "last_msg_id": last_msg.id,
                "lastMessage": last_message_text,
                "time": last_msg.date_time.isoformat(),
                "status": recipient.status,
                "last_seen": recipient.last_seen.isoformat(),
                "unread": unread,
                "task": task_info,
                "assignment": assignment_info
            })


        cache.set(cache_key, result)
        return result

class ChatResource(Resource):
    @jwt_required()
    def get(self, conversation_id):
        user_id = get_jwt_identity()
        cache = current_app.cache
        cache_key = f"chat_{conversation_id}_{user_id}"

        # Check cache
        cached_chat = cache.get(cache_key)
        if cached_chat:
            return cached_chat
        
        # Fetch conversation
        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            return {"message": "Conversation not found"}, 404
        
        # Determine recipient
        if conversation.task_giver != user_id:
            recipient_id = conversation.task_giver
        else:
            recipient_id = conversation.task_doer

        user = User.query.get(recipient_id)

        # Fetch related task and assignment
        task = Task.query.get(conversation.task_id)
        assignment = TaskAssignment.query.filter_by(task_id=conversation.task_id).first()

        # Fetch last 20 messages
        messages = (
            Message.query
            .filter_by(conversation_id=conversation_id)
            .order_by(Message.date_time.desc())
            .limit(20)
            .all()
        )
        messages.reverse()  # oldest first

        # Build response
        response = {
            "user_info": {
                "id": user.id,
                "name": user.name,
                "avator": user.image,
                "status": user.status,
                "last_seen": user.last_seen.isoformat()
            },
            "archived": conversation.archived,
            "messages": [
                {
                    "message_id": msg.id,
                    "sender_id": msg.sender_id,
                    "receiver_id": msg.reciever_id,
                    "text": msg.message,
                    "image": msg.image,
                    "time": msg.date_time.isoformat(),
                    "status": msg.status,
                    "sent": int(msg.sender_id) == int(user_id)
                }
                for msg in messages
            ],
            "task": {
                "title": task.title if task else None,
                "description": task.description if task else None,
                "status": task.status if task else None
            },
            "assignment": {
                "agreed_price": float(assignment.agreed_price) if assignment else None,
                "status": assignment.status if assignment else None
            } if assignment else {}
        }

        # Cache and return
        cache.set(cache_key, response)
        return response

# /messages/<conversation_id>?offset=0&limit=10
class OlderMessages(Resource):
    @jwt_required()
    def get(self, conversation_id):
        offset = int(request.args.get('offset', 10))
        limit = int(request.args.get('limit', 20))
        user_id = get_jwt_identity()

        cache = current_app.cache
        cache_key = f"older_msgs_{conversation_id}_{offset}_{limit}"

        # Check cache first
        # cached_msgs = cache.get(cache_key)
        # if cached_msgs:
        #     return cached_msgs

        # Fetch from DB if not cached
        messages = (
            Message.query
            .filter_by(conversation_id=conversation_id)
            .order_by(Message.date_time.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        

        response = [
            {
                "message_id": msg.id,
                "sender_id": msg.sender_id,
                "receiver_id": msg.reciever_id,
                "text": msg.message,
                "image": msg.image,
                "time": msg.date_time.isoformat(),
                "status": msg.status,
                "sent": int(msg.sender_id) == int(user_id)
            }
            for msg in messages
        ]

        # Cache the result (optional: set a TTL if needed)
        cache.set(cache_key, response)

        return response
