from flask_restful import Resource, reqparse
from flask import jsonify
from decimal import Decimal
from utils.ledgers.platform import FloatLedger

class TestFloatLedger(Resource):
    def get(self):
        args = {
            'reference': 'TEST123456',
            'direction': 'out',
            'amount': 99.00,
            'source': 'M-Pesa',
            'destination': 'platform wallet',
            'purpose': 'Initial top-up',
            'status': 'success'
        }


        # Create a FloatLedger instance
        ledger = FloatLedger(
            reference=args['reference'],
            direction=args['direction'],
            amount=Decimal(str(args['amount'])),
            source=args.get('source'),
            destination=args.get('destination'),
            purpose=args.get('purpose'),
            status=args.get('status')
        )

        # Call ledge() to save to DB
        try:
            ledger.ledge()
            return {"message": "Float ledger entry created successfully."}
        except Exception as e:
            return {"error": str(e)}, 500
