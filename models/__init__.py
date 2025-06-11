from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

# Configure naming convention for constraints
metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})

db = SQLAlchemy(metadata=metadata)

# Import models so they are registered with SQLAlchemy
from models.user import User
from models.user_info import UserInfo
from models.category import Category
from models.task_location import TaskLocation
from models.task import Task
from models.task_assignment import TaskAssignment
from models.bid import Bid
from models.notification import Notification
from models.task_image import TaskImage
from models.review import Review
from models.conversation import Conversation
from models.message import Message
from models.push_subscription import PushSubscription
from models.audit_logs import AuditLog
from models.currencies import Currency
from models.escrow_actions import EscrowAction
from models.escrow import Escrow
from models.fees import Fee
from models.platform_wallet import PlatformWallet
from models.transactions import Transaction
from models.user_wallet import Wallet
from models.payment_details import PaymentDetail
from models.feedback import Feedback
from models.FloatWalletLedger import FloatWalletLedger
from models.transaction_ledger import TransactionLedger
from models.wallet_transactions import WalletTransaction