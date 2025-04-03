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
            task_giver=task_giver_id,
            task_doer=task_doer_id,
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
            # Check who the recipient is based on the user_id
            if convo.task_giver == user_id:
                recipient_user_id = convo.task_doer
            else:
                recipient_user_id = convo.task_giver

            # Get the user data of the recipient
            recipient = User.query.get(recipient_user_id)

            # Get the last message in the conversation
            last_msg = Message.query.filter_by(conversation_id=convo.id).order_by(Message.date_time.desc()).first()
            last_msg_id = last_msg.id if last_msg else None
            last_message = last_msg.message if last_msg else None

            # If the passed user_id sent the last message, prepend "You: "
            if last_msg and ((last_msg.task_giver == user_id) or (last_msg.task_doer == user_id)):
                last_message = f"You: {last_message}"

            result.append({
                "conversation_id": convo.id,
                "task_giver": convo.task_giver,
                "task_doer": convo.task_doer,
                "recipient": {
                    "user_id": recipient.id,
                    "name": recipient.name,
                    "profile_image": recipient.image  # Assuming profile image URL is stored in 'image'
                },
                "last_msg_id": last_msg_id,
                "last_message": last_message
            })

        try:
            return result
        except TypeError as e:
            return {"message": f"Error serializing data: {str(e)}"}, 500