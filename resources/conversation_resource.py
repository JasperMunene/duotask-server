# task_resource.py
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from flask import current_app, jsonify, request
from models.conversation import Conversation
from models.message import Message
from models.user import User
from models import db
import datetime

class ConversationResource(Resource):
    def post(self):        
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

        return {"message": "Conversation created successfully", "conversation_id": conversation.id}, 201

    def get(self, user_id):
        # Get all conversations where the user is either task_giver or task_doer
        conversations = Conversation.query.filter(
            (Conversation.task_giver == user_id) | (Conversation.task_doer == user_id)
        ).all()

        result = []
        for convo in conversations:
            # Determine the recipient user
            recipient_user_id = convo.task_doer if convo.task_giver == user_id else convo.task_giver
            recipient = User.query.get(recipient_user_id)

            # Get the last message in the conversation
            last_msg = (
                Message.query
                .filter_by(conversation_id=convo.id)
                .order_by(Message.date_time.desc())
                .first()
            )

            # Get the last 5 messages
            last_10_msgs = (
                Message.query
                .filter_by(conversation_id=convo.id)
                .order_by(Message.date_time.desc())
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


            # If the passed user_id sent the last message, prepend "You: "
            last_message = f"You: {last_msg.message}" if last_msg and last_msg.sender_id == user_id else last_msg.message if last_msg else None
            
            unread = False if last_msg and last_msg.reciever_id and last_msg.status == "read" else True 
            
            result.append({
                "id": convo.id,
                "task_giver": convo.task_giver,
                "task_doer": convo.task_doer,
                "recipient": {
                    "user_id": recipient.id,
                    "name": recipient.name,
                    "avator": recipient.image  # Assuming profile image URL is stored in 'image'
                },
                "messages": messages,
                "last_msg_id": last_msg.id if last_msg else None,
                "lastMessage": last_message,
                "time": last_msg.date_time.isoformat(),
                "unread": unread
            })

        try:
            return result
        except TypeError as e:
            return {"message": f"Error serializing data: {str(e)}"}, 500
