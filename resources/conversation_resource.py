# task_resource.py
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app, request
from models.conversation import Conversation
from models.message import Message
from models.user import User
from flask import current_app
from models import db
import datetime

class ConversationResource(Resource):
    def post(self):        
        cache = current_app.cache
        data = request.get_json()
        task_giver_id = data.get('task_giver_id')
        task_doer_id = data.get('task_doer_id')
        # Ensure that both task_giver and task_doer are valid users
        task_giver = User.query.get(task_giver_id)
        task_doer = User.query.get(task_doer_id)
        
        if not task_giver or not task_doer:
            return {"message": "Invalid user IDs"}, 400

        # Create a new conversation
        conversation = Conversation(task_giver=task_giver_id, task_doer=task_doer_id)

        # Create the default message for task_doer
        message = Message(
            conversation=conversation,
            sender_id=task_giver_id,
            reciever_id=task_doer_id,
            message="Hello, let's start the conversation.",
            date_time=db.func.now()
        )

        # Add the conversation and the message to the session and commit
        db.session.add(conversation)
        db.session.add(message)
        db.session.commit()
        cache.delete(f"conversations_user_{task_giver_id}")
        cache.delete(f"conversations_user_{task_doer_id}")
        return {"message": "Conversation created successfully", "conversation_id": conversation.id}, 201

    def get(self, user_id):
        cache = current_app.cache
        cache_key = f"conversations_user_{user_id}"

        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

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
                .limit(10)
                .all()
            )



            # Format messages
            messages = [
                {
                    "message_id": msg.id,
                    "sender_id": msg.sender_id,
                    "receiver_id": msg.reciever_id,
                    "text": msg.message,
                    "time": msg.date_time.isoformat(),
                    "status": msg.status,
                    "sent": msg.sender_id == user_id  # True if sender_id matches user_id, else False
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

            last_message_text = f"You: {last_msg.message}" if last_msg.sender_id == user_id else last_msg.message
            unread = last_msg.reciever_id == user_id and last_msg.status != "read"

            result.append({
                "id": convo.id,
                "task_giver": convo.task_giver,
                "task_doer": convo.task_doer,
                "recipient": {
                    "user_id": recipient.id,
                    "name": recipient.name,
                    "avator": recipient.image
                },
                "messages": messages,
                "last_msg_id": last_msg.id,
                "lastMessage": last_message_text,
                "time": last_msg.date_time.isoformat(),
                "status": recipient.status,
                "last_seen": recipient.last_seen.isoformat(),
                "unread": unread
            })

        cache.set(cache_key, result)
        return result

# /messages/<conversation_id>?offset=0&limit=10
class OlderMessages(Resource):
    @jwt_required()
    def get(self, conversation_id):
        offset = int(request.args.get('offset', 0))
        limit = int(request.args.get('limit', 10))
        user_id = get_jwt_identity()

        cache = current_app.cache
        cache_key = f"older_msgs_{conversation_id}_{offset}_{limit}"

        # Check cache first
        cached_msgs = cache.get(cache_key)
        if cached_msgs:
            return cached_msgs

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
                "time": msg.date_time.isoformat(),
                "status": msg.status,
                "sent": msg.sender_id == user_id
            }
            for msg in messages
        ]

        # Cache the result (optional: set a TTL if needed)
        cache.set(cache_key, response)

        return response
