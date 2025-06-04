from flask import current_app, request
from extensions import socketio
from models.user import User
from models.conversation import Conversation
from models.message import Message
from models import db
from utils.send_notification import Notify
import logging
logger = logging.getLogger()

@socketio.on('connect')
def handle_connect():
    """Handle user connections and notify relevant users efficiently."""
    user_id = request.args.get('user_id')

    if user_id:
        with current_app.app_context():  # Ensuring we have the correct app context
            cache = current_app.cache
            redis = current_app.redis
            cache.set(f"user_sid:{user_id}", request.sid, timeout=0)
            redis.sadd("online_users", user_id)  # Track online user
            print(f"[+] User {user_id} connected with SID {request.sid}")

        user = User.query.get(user_id)
        if user:
            user.update_status("online")
            print(f"[✓] User {user_id} status set to online")

            conversations = Conversation.query.filter(
                (Conversation.task_giver == user_id) | (Conversation.task_doer == user_id)
            ).all()

            other_user_ids = {
                str(convo.task_doer) if str(convo.task_giver) == user_id else str(convo.task_giver)
                for convo in conversations
            }

            if not other_user_ids:
                print(f"[ℹ️] User {user_id} has no conversation participants")
                return

            other_users = User.query.filter(User.id.in_(other_user_ids)).all()
            online_users = [user for user in other_users if user.status == "online"]

            if not online_users:
                print(f"[ℹ️] No online users to notify about user {user_id}'s connection")
                return

            for u in online_users:
                sid = cache.get(f"user_sid:{str(u.id)}")
                if sid:
                    socketio.emit('user_connected', {'user_id': user_id}, room=sid)
                    print(f"[📢] Notified user {u.id} (SID: {sid}) that user {user_id} is online")
                else:
                    print(f"[🚫] User {u.id} is online in DB but not connected via socket")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle user disconnections and notify relevant users efficiently."""
    disconnected_user_id = None
    user_id = request.args.get('user_id')
    with current_app.app_context():  # Ensuring cache access inside app context
        # Retrieve the online users from the cache
        online_users = current_app.redis.smembers("online_users")
        
        if online_users is None:
            online_users = []  # Initialize as an empty list if it's not found in cache
        print(f"Current online users: {online_users}")

        # Iterate over all online users
        for user_id in online_users:
            sid = current_app.cache.get(f"user_sid:{user_id}")
            print(f"Checking user {user_id}, SID: {sid} against request SID: {request.sid}")
            if sid == request.sid:
                disconnected_user_id = user_id
                # Remove the user's SID from the cache
                current_app.cache.delete(f"user_sid:{user_id}")
                # Remove the user ID from the online_users list in the cache
                # online_users.remove(user_id)
                current_app.redis.srem("online_users", user_id)  # Save the updated list back in the cache
                print(f"Updated online users: {online_users}")
                break

    if not disconnected_user_id:
        print("[⚠️] Could not find disconnected user in session list")
        return

    print(f"[-] User {disconnected_user_id} disconnected with SID {request.sid}")

    user = User.query.get(disconnected_user_id)
    if user:
        user.update_status("offline")
        print(f"[✓] User {disconnected_user_id} status set to offline")

        conversations = Conversation.query.filter(
            (Conversation.task_giver == disconnected_user_id) | (Conversation.task_doer == disconnected_user_id)
        ).all()
        print(f"Conversations found for user {disconnected_user_id}: {conversations}")

        other_user_ids = {
            str(convo.task_doer) if str(convo.task_giver) == disconnected_user_id else str(convo.task_giver)
            for convo in conversations
        }

        if not other_user_ids:
            print(f"[ℹ️] User {disconnected_user_id} had no conversation participants")
            return

        other_users = User.query.filter(User.id.in_(other_user_ids)).all()
        online_users = [u for u in other_users if u.status == "online"]
        print(f"Online users to notify: {online_users}")

        if not online_users:
            print(f"[ℹ️] No online users to notify about user {disconnected_user_id}'s disconnection")
            return

        for u in online_users:
            sid = current_app.cache.get(f"user_sid:{str(u.id)}")
            if sid:
                socketio.emit('user_disconnected', {'user_id': disconnected_user_id}, room=sid)
                print(f"[📢] Notified user {u.id} (SID: {sid}) that user {disconnected_user_id} went offline")
            else:
                print(f"[🚫] User {u.id} is online in DB but not connected via socket")

@socketio.on('send_message')
def handle_send_message(data):
    """Handle when a user sends a message."""
    sender_id = request.args.get('user_id')
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
        date_time=db.func.now(),
        status="sent"
    )

    db.session.add(new_message)
    db.session.commit()

    
    # Handle cache access within app context
    with current_app.app_context():
        # Check if receiver is online
        sender_sid = current_app.cache.get(f"user_sid:{sender_id}")
        if sender_sid:
            socketio.emit('message_sent', {
                'conversation_id': conversation_id,
                'message_id': new_message.id,
                'status': "sent",
                'success': True
            }, room=sender_sid)
        print('message sent')
        current_app.cache.delete(f"conversations_user_{receiver_id}")
        current_app.cache.delete(f"conversations_user_{sender_id}")
        receiver_sid = current_app.cache.get(f"user_sid:{receiver_id}")
        Notify(user_id=receiver_id, message="You got a new message", source="chat", sender_id=sender_id).post()
        if receiver_sid:
            # Update message status to delivered
            message = Message.query.get(new_message.id)
            message.status = "delivered"
            db.session.commit()

            # Emit to receiver
            socketio.emit('receive_message', {
                'conversation_id': conversation_id,
                'message_id': new_message.id,
                'message': new_message.message,
                'sender_id': int(sender_id),
                'time': new_message.date_time.isoformat()
            }, room=receiver_sid)
            
            status = "delivered"
            # Emit to sender about the message status
            socketio.emit('message_status_update', {
                    'conversation_id': conversation_id,
                    'message_id': new_message.id,
                    'status': status
                }, room=sender_sid)

            print(f"📨 Message from {sender_id} to {receiver_id}: {message_text} | Status: {status}")
    

@socketio.on('message_status')
def handle_message_status(data):
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

        # Handle cache access within app context
        with current_app.app_context():
            # Notify the sender about the message status update
            sender_id = message.sender_id
            sender_sid = current_app.cache.get(f"user_sid:{sender_id}")  # Get the sender's SID from cache
            
            if sender_sid:
                socketio.emit('message_status_update', {
                    'conversation_id': conversation_id,
                    'message_id': message_id,
                    'status': status
                }, room=sender_sid)
                print(f"Message {message_id} status updated to {status} for sender {sender_id}")
            else:
                print(f"Sender {sender_id} is not online (SID not found)")

    except Exception as e:
        print(f"Error updating status: {e}")
        db.session.rollback()


@socketio.on('typing')
def handle_typing(data):
    """Handle typing indicators."""
    try:
        user_id = int(request.args.get('user_id'))
        conversation_id = data.get('conversation_id')
        receiver_id = data.get('receiver_id')
        is_typing = data.get('is_typing', False)

        if not user_id or not conversation_id:
            return

        if receiver_id:
            other_user_id = receiver_id
        else:
            conversation = db.session.query(
                Conversation.task_giver, Conversation.task_doer
            ).filter_by(id=conversation_id).first()
            
            if not conversation:
                return

            other_user_id = (
                str(conversation.task_doer) if conversation.task_giver == user_id
                else str(conversation.task_giver)
            )

        with current_app.app_context():
            other_user_sid = current_app.cache.get(f"user_sid:{other_user_id}")
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
    """Mark all messages in a conversation as delivered for the current user."""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return

    try:
        # Fetch all undelivered messages for this user
        unread_messages = Message.query.filter_by(
            reciever_id=user_id,
            status='sent'  # Messages not marked as delivered yet
        ).all()

        # Update their status to "delivered"
        for message in unread_messages:
            message.status = 'delivered'
        
        db.session.commit()

        print(f"[✓] Marked {len(unread_messages)} messages as delivered for user {user_id}")

        # Optionally notify the sender(s)
        with current_app.app_context():
            for message in unread_messages:
                sender_sid = current_app.cache.get(f"user_sid:{message.sender_id}")
                if sender_sid:
                    socketio.emit('message_status_update', {
                        'conversation_id': message.conversation_id,
                        'message_id': message.id,
                        'status': 'delivered'
                    }, room=sender_sid)
    
    except Exception as e:
        db.session.rollback()
        print(f"[❌] Error marking messages as delivered for user {user_id}: {e}")
