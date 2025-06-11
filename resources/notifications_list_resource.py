from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.user import User
from models.notification import Notification

# SOURCE -> IMAGE & LINK
SOURCE_DETAILS = {
    "order": {
        "image": "/static/images/order.png"
    },
    "wallet": {
        "image": "https://cdn-icons-png.flaticon.com/512/6020/6020687.png",
    },
    "promotion": {
        "image": "/static/images/promo.png"
    },
    "system": {
        "image": "/static/images/system.png"
    },
    "default": {
        "image": "https://static-00.iconduck.com/assets.00/profile-default-icon-1024x1023-4u5mrj2v.png"
    }
}

class NotificationsListResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return {"message": "User not found"}, 404

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        notifications_query = Notification.query \
            .filter(Notification.user_id == user_id, Notification.source != 'chat') \
            .order_by(Notification.created_at.desc())


        pagination = notifications_query.paginate(page=page, per_page=per_page, error_out=False)
        notifications = pagination.items

        notification_list = []
        for notification in notifications:
            source_data = SOURCE_DETAILS.get(notification.source.lower(), SOURCE_DETAILS["default"])

            if notification.sender_id is None:
                sender = {
                    "name": notification.source.capitalize(),
                    "source": notification.source,
                    "image": source_data["image"],
                    "link": None
                }
            else:
                sender_user = User.query.get(notification.sender_id)
                sender = {
                    "name": sender_user.name if sender_user else f"Sender {notification.sender_id}",
                    "source": notification.source,
                    "image": sender_user.image if sender_user else source_data["image"]
                }

            notification_list.append({
                "id": notification.id,
                "message": notification.message,
                "is_important": notification.is_important,
                "is_read": notification.is_read,
                "created_at": notification.created_at.isoformat(),
                "sender": sender
            })

        return {
            "notifications": notification_list,
            "total": pagination.total,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "pages": pagination.pages
        }, 200

class MarkNotificationRead(Resource):
    @jwt_required()
    def post(self, notification_id):
        user_id = get_jwt_identity()
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()

        if not notification:
            return {"message": "Notification not found"}, 404

        notification.is_read = True
        db.session.commit()

        return {"message": "Notification marked as read"}, 200