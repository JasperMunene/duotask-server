# from flask_restful import Resource, reqparse
# from flask import jsonify
# from decimal import Decimal
# from utils.ledgers.platform import FloatLedger
# from workers.instant_recomendation import recommend_best_user_for_task
# from utils.recommendation_queue import add_task_to_batch

# class TestFloatLedger(Resource):
#     def post(self):
#         # args = {
#         #     'reference': 'TEST123456',
#         #     'direction': 'out',
#         #     'amount': 99.00,
#         #     'source': 'M-Pesa',
#         #     'destination': 'platform wallet',
#         #     'purpose': 'Initial top-up',
#         #     'status': 'success'
#         # }


#         # # Create a FloatLedger instance
#         # ledger = FloatLedger(
#         #     reference=args['reference'],
#         #     direction=args['direction'],
#         #     amount=Decimal(str(args['amount'])),
#         #     source=args.get('source'),
#         #     destination=args.get('destination'),
#         #     purpose=args.get('purpose'),
#         #     status=args.get('status')
#         # )

#         # # Call ledge() to save to DB
#         # try:
#         #     ledger.ledge()
#         #     return {"message": "Float ledger entry created successfully."}
#         # except Exception as e:
#         #     return {"error": str(e)}, 500

#         task_id = 82
#         self._send_recommendation(task_id)
    
#         # add_task_to_batch(task_id)
#     def _send_recommendation(self, task_id):
#         """
#         Send a recommendation for the best user to assign to a task.
#         """
#         try:
#             # recommend_best_user_for_task.delay(task_id)
#             add_task_to_batch(task_id)
#             return {"message": "Recommendation sent successfully."}, 200
#         except Exception as e:
#             return {"error": str(e)}, 500

from flask_restful import Resource, reqparse
from flask import jsonify
from utils.recommendation_queue import add_task_to_batch

class TestFloatLedger(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('task_id', type=int, required=True, help='task_id is required')
        args = parser.parse_args()
        task_id = args['task_id']

        return self._send_recommendation(task_id)

    def _send_recommendation(self, task_id):
        """
        Add task to batch recommendation queue.
        """
        try:
            add_task_to_batch(task_id)
            return {"message": f"Task {task_id} added to batch recommendation queue."}, 200
        except Exception as e:
            return {"error": str(e)}, 500
