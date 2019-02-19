from logger import Logger

logger = Logger('scores.csv', 'orders.csv')

s, m = logger.read_scores_file()
print('Scores:')
print(s)
print('Multipliers:')
print(m)
b = logger.read_orders_file()
print('Orders:')
print(b)