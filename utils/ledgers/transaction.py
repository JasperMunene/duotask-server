from models.transaction_ledger import TransactionLedger
from flask import current_app
from decimal import Decimal
from models import db

class TransactionLedg():
    def __init__(self, reference, sender_id=None, receiver_id=None, system=None, amount=Decimal('0.00'), type=None, status=None, description=None):
        self.reference = reference
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.system = system
        self.amount = amount if amount is not None else Decimal('0.00')
        self.type = type
        self.status = status
        self.description = description
        
    def ledge(self):
        reference = self.reference
        sender_id = self.sender_id
        receiver_id = self.receiver_id
        system = self.system
        amount  =self.amount
        type = self.type
        status =self.status
        description = self.description
        
        transaction = TransactionLedger(
            reference = reference,
            sender_id = sender_id,
            reciever_id = receiver_id,
            system = system,
            amount  = amount,
            type = type,
            status =status,
            description = description
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        print ("created ")