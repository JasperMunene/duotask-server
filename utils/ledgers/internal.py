from decimal import Decimal
from models import db
from models.user_wallet import Wallet
from models.internal_transactions import InternalTransaction
from models.platform_wallet import PlatformWallet
from utils.send_notification import Notify
from utils.exceptions import InsufficientBalanceError
import uuid
import logging

logger = logging.getLogger(__name__)


class InternalTransfer:
    PLATFORM_FEE_RATE = Decimal("0.15")

    def __init__(self, task_id, task_title, user_id, doer_id, amount):
        self.task_id = task_id
        self.task_title = task_title
        self.user_id = user_id
        self.doer_id = doer_id
        self.amount = Decimal(amount)
        self.platform_fee = (self.amount * self.PLATFORM_FEE_RATE).quantize(Decimal("0.01"))
        self.reference = f"task_{task_id}_{uuid.uuid4().hex[:10]}"

    def hold_funds(self):
        try:
            wallet = Wallet.query.filter_by(user_id=self.user_id).first()
            if not wallet or wallet.balance < self.amount:
                 raise InsufficientBalanceError(required_amount=self.amount, current_balance=0)
            
            current_balance = Decimal(wallet.balance)
            required_amount = Decimal(self.amount)

            if current_balance < required_amount:
                raise InsufficientBalanceError(required_amount=required_amount, current_balance=current_balance)

            # Deduct from user wallet
            wallet.balance -= required_amount

            # Log internal transaction
            txn = InternalTransaction(
                task_id=self.task_id,
                reference=self.reference,
                user_id=self.user_id,
                doer_id=self.doer_id,
                amount=self.amount,
                platform_fee=self.platform_fee,
                status="held"
            )
            db.session.add(txn)
            db.session.commit()

            # Notify user
            message = (
                f"You've been charged KES {float(self.amount):,.2f} for the task '{self.task_title}'. "
                f"The funds are held securely and will be released when the task is completed."
            )
            Notify(
                user_id=self.user_id,
                message=message,
                source="wallet",
                is_important=True,
                sender_id=None
            ).post()

            return {"status": "success", "reference": self.reference}

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error holding funds: {e}", exc_info=True)
            raise

    def release_funds(self):
        try:
            txn = (
                InternalTransaction.query
                .filter_by(task_id=self.task_id, status="held")
                .with_for_update()
                .first()
            )
            if not txn:
                raise ValueError("No held transaction found for release")

            doers_pay = txn.amount - txn.platform_fee

            # Get or create doer's wallet
            doer_wallet = Wallet.query.filter_by(user_id=self.doer_id).with_for_update().first()
            if not doer_wallet:
                doer_wallet = Wallet(user_id=self.doer_id, balance=Decimal("0.00"), status="active")
                db.session.add(doer_wallet)

            doer_wallet.balance += doers_pay

            # Get or create platform wallet
            platform_wallet = PlatformWallet.query.first()
            if not platform_wallet:
                platform_wallet = PlatformWallet(balance=Decimal("0.00"), status="active")
                db.session.add(platform_wallet)

            platform_wallet.balance = (platform_wallet.balance or Decimal("0.00")) + txn.platform_fee

            # Update transaction status
            txn.status = "released"

            db.session.commit()

            # Notify doer
            message = (
                f"You have received KES {float(doers_pay):,.2f} for completing the task '{self.task_title}'. "
                f"The funds are now visible in your wallet."
            )
            Notify(
                user_id=self.doer_id,
                message=message,
                source="wallet",
                is_important=True,
                sender_id=None
            ).post()

            return {
                "status": "success",
                "doer_pay": float(doers_pay),
                "platform_fee": float(txn.platform_fee)
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error releasing funds: {e}", exc_info=True)
            raise
