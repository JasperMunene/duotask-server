from flask import request
from extensions import socketio
from models.user import User
from models.conversation import Conversation
from models.message import Message
from models import db
from datetime import datetime

# Dictionary to track user sessions (user_id => session_id)
user_sessions = {}

@socketio.on('connect')
def handle_connect():
    """Handle user connections and store their SID."""
    user_id = request.args.get('user_id')
    if user_id:
        user_sessions[user_id] = request.sid  # Store the SID for the user
        user = User.query.get(user_id)
        if user:
            user.update_status("online")
            socketio.emit('user_connected', {'user_id': user_id})

        print(f"User {user_id} connected with SID {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle user disconnections and remove their SID."""
    for user_id, sid in user_sessions.items():
        if sid == request.sid:
            del user_sessions[user_id]
            print(f"User {user_id} disconnected.")
            user = User.query.get(user_id)
            if user:
                user.update_status("offline")
                socketio.emit('user_disconnected', {'user_id': user_id})

            break

@socketio.on('send_message')
def handle_send_message(data):
    """Handle when a user sends a message."""
    sender_id = request.args.get('user_id')  # Get user ID from the query string
    receiver_id = data.get('receiver_id')
    conversation_id = data.get('conversation_id')
    message_text = data.get('message')

    if not sender_id or not receiver_id or not message_text:
        socketio.emit('message_error', {'message': 'Missing required fields'})
        return

    conversation = Conversation.query.get(conversation_id)
    if not conversation:
        socketio.emit('message_error', {'message': 'Conversation not found'})
        return

    
    new_message = Message(
        conversation=conversation,
        sender_id=sender_id,
        reciever_id=receiver_id,
        message=message_text,
        date_time=db.func.now()
    )

    
    
    db.session.add(new_message)
    db.session.commit()

    # Send message to receiver if online
    other_user_id = str(conversation.task_doer) if int(conversation.task_giver) == int(sender_id) else str(conversation.task_giver)
    other_user_sid = user_sessions.get(other_user_id)
    if other_user_sid:
        status = "delivered"
        # if online update the status to delivered
        message = Message.query.get(new_message.id)        
        # Update message status
        message.status = "delivered"
        db.session.commit()
        socketio.emit('receive_message', {
            'conversation_id': conversation_id,
            'message_id': new_message.id,
            'message': new_message.message,
            'sender_id': sender_id,
            'time': new_message.date_time.isoformat()
        }, room=[other_user_sid])
        print(f"reciever request sent from {sender_id} to {receiver_id}: {message_text}")
    else: 
        status = "sent"
        print ("no user found with that id")
    # Confirm message delivery to sender
    socketio.emit('message_sent', {
        'conversation_id': conversation_id,
        'message_id': new_message.id,
        'status': status,
        'success': True
    }, room=user_sessions.get(sender_id))

    print(f"Message sent from {sender_id} to {receiver_id}: {message_text}")

@socketio.on('message_status')
def handle_message_read(data):
    """Handle updating message status."""
    user_id = request.args.get('user_id')
    conversation_id = data.get('conversation_id')
    message_id = data.get('message_id')
    status = data.get('status')
    if not user_id or not conversation_id or not message_id:
        return
    
    try:
        # Get the message
        message = Message.query.get(message_id)
        
        if not message:
            return
        
        # Update message status
        message.status = status
        db.session.commit()
        sender_id = message.sender_id
        sender_sid = user_sessions.get(str(sender_id))  # Get the sender's SID
        if sender_sid:
            socketio.emit('message_status_update', {
                'conversation_id': conversation_id,
                'message_id': message_id,
                'status': status
            }, room=sender_sid)
            print(f"status update to {status} to {sender_id}")

    except Exception as e:
        print(f"Error updating status: {e}")
        db.session.rollback()

@socketio.on('typing')
def handle_typing(data):
    """Handle typing indicators."""
    user_id = request.args.get('user_id')
    conversation_id = data.get('conversation_id')
    is_typing = data.get('is_typing', False)
    
    if not user_id or not conversation_id:
        return
    
    try:
        conversation = Conversation.query.get(conversation_id)
        
        if not conversation:
            return
        
        # Determine the other user in this conversation
        other_user_id = str(conversation.task_doer) if int(conversation.task_giver) == int(user_id) else str(conversation.task_giver)
        
        other_user_sid = user_sessions.get(other_user_id)  # Get the other user's SID
        if other_user_sid:
            socketio.emit('typing_indicator', {
                'conversation_id': conversation_id,
                'user_id': user_id,
                'is_typing': is_typing
            }, room=other_user_sid)
            
    except Exception as e:
        print(f"Error with typing indicator: {e}")


@socketio.on('mark_conversation_read')
def handle_mark_all_delivered():
    """Mark all messages in a conversation as read."""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return
    
    try:
        unread_messages = Message.query.filter_by(
            receiver_id=user_id,
            status__in=['sent']  # Messages that are not read yet
        ).all()
        
        for message in unread_messages:
            message.status = "delivered"
        
        db.session.commit()
            
    except Exception as e:
        print(f"Error marking conversation as read: {e}")
        db.session.rollback()
