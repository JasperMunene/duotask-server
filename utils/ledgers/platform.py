from models.FloatWalletLedger import FloatWalletLedger
from flask import current_app
from decimal import Decimal
from models import db
# import Logger
import logging
logger = logging.getLogger()

class FloatLedger():
    def __init__(self, reference, direction=None, amount=None, source=None, destination=None, purpose=None, status=None):
        self.reference = reference
        self.direction = direction if direction is not None else None
        self.amount = amount if amount is not None else None
        self.source = source if source is not None else None
        self.destination = destination if destination is not None else None
        self.purpose = purpose if purpose is not None else None
        self.status = status if status is not None else None
                
    def ledge(self):
        reference = self.reference
        direction = self.direction
        amount = self.amount
        source = self.source
        destination = self.destination
        purpose = self.purpose
        status = self.status
        
        # Get the last known balance
        last_entry = FloatWalletLedger.query.order_by(FloatWalletLedger.id.desc()).first()
        previous_balance = last_entry.balance if last_entry else Decimal('0.00')

        # Calculate new balance
        if direction == 'in':
            new_balance = previous_balance + amount
        else:
            new_balance = previous_balance - amount

        # Create the ledger entry
        ledger = FloatWalletLedger(
            reference=reference,
            direction=direction,
            amount=amount,
            source=source,
            destination=destination,
            purpose=purpose,
            status=status,
            balance=new_balance
        )

        # Save to DB
        db.session.add(ledger)
        db.session.commit()    

        print("Float transaction ledged successfully")
        logger.info(f"Float transaction {reference} created with amount {amount} and direction {direction}")       