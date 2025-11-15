from flask import request
from flask_restful import Resource
from services.email_service import send_email
from utils.templates.email_templates import wallet_authorization_email_template, wallet_topup_email_template
from datetime import datetime
from workers.email_worker import send_wallet_top_up_mail

class TestWalletAuthorizationEmail(Resource):
    def post(self):
        """
        Test endpoint for wallet authorization email
        
        Expected JSON body:
        {
            "recipient_email": "esliehh@gmail.com",
            "name": "John Doe",
            "amount": 2500.00,
            "task_name": "Plumbing Repair - Kitchen Sink",
            "task_id": "TASK-2025-001234",
            "worker_name": "Jane Kamau",
            "worker_phone": "+254 712 345 678",
            "worker_profile_image": "https://example.com/profile.jpg"
        }
        """
        try:
            data = request.get_json()
            
            # Extract data with defaults
            recipient_email = data.get('recipient_email')
            name = data.get('name', 'Test User')
            amount = float(data.get('amount', 2500.00))
            task_name = data.get('task_name', 'Test Task')
            task_id = data.get('task_id', f'TASK-{datetime.now().strftime("%Y%m%d%H%M%S")}')
            worker_name = data.get('worker_name', 'John Worker')
            worker_phone = data.get('worker_phone', '+254 712 345 678')
            worker_profile_image = data.get('worker_profile_image', 
                'https://ui-avatars.com/api/?name=John+Worker&size=200&background=00915a&color=fff')
            
            if not recipient_email:
                return {'error': 'recipient_email is required'}, 400
            
            # Generate timestamp
            timestamp = datetime.now().strftime("%b %d, %Y at %I:%M %p")
            
            # Generate email HTML
            email_html = wallet_authorization_email_template(
                name=name,
                amount=amount,
                task_name=task_name,
                task_id=task_id,
                worker_name=worker_name,
                worker_phone=worker_phone,
                worker_profile_image=worker_profile_image,
                timestamp=timestamp
            )
            
            # Send email
            send_email(
                to_email=recipient_email,
                subject=f"Payment Authorized - {task_name}",
                html_content=email_html
            )
            
            return {
                'success': True,
                'message': 'Wallet authorization email sent successfully',
                'details': {
                    'recipient': recipient_email,
                    'task_id': task_id,
                    'amount': amount,
                    'timestamp': timestamp
                }
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500


class TestWalletTopupEmail(Resource):
    def post(self):
        """
        Test endpoint for wallet top-up email
        
        Expected JSON body:
        {
            "recipient_email": "esliehh@gmail.com",
            "name": "John Doe",
            "amount": 5000.00,
            "transaction_id": "TXN-2025-001234",
            "payment_method": "M-Pesa"
        }
        """
        try:
            data = request.get_json()
            
            # Extract data with defaults
            recipient_email = data.get('recipient_email')
            name = data.get('name', 'Test User')
            amount = float(data.get('amount', 5000.00))
            transaction_id = data.get('transaction_id', f'TXN-{datetime.now().strftime("%Y%m%d%H%M%S")}')
            payment_method = data.get('payment_method', 'M-Pesa')
            
            if not recipient_email:
                return {'error': 'recipient_email is required'}, 400
            
            # Generate timestamp
            timestamp = datetime.now().strftime("%b %d, %Y at %I:%M %p")
            
            send_wallet_top_up_mail.delay(
                user_id = 41,  # Dummy user_id for testing
                amount = amount,
                transaction_id = transaction_id
            )
            
            return {
                'success': True,
                'message': 'Wallet top-up email sent successfully',
                'details': {
                    'recipient': recipient_email,
                    'transaction_id': transaction_id,
                    'amount': amount,
                    'timestamp': timestamp
                }
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

