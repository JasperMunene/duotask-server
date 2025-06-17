# utils/exceptions.py
class InsufficientBalanceError(Exception):
    def __init__(self, required_amount, current_balance):
        self.required_amount = required_amount
        self.current_balance = current_balance
        super().__init__("Insufficient balance")
