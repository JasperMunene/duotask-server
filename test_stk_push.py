from utils.payment import GetFunds

user_id = 23
amount = 10
transaction_id = 123
GetFunds(user_id, amount, transaction_id).post()