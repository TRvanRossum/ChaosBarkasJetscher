import csv

class Logger:

    scores_file = ''
    orders_file = ''

    def __init__(self, _scores_f, _orders_f):
        self.scores_file = _scores_f
        self.orders_file = _orders_f

    def write_scores_file(self, scores, multiplier):
        try:
            with open('scores.csv', 'w', newline='') as csvfile:
                fieldnames = ['groep', 'score', 'multiplier']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for g, s in scores.items():
                    writer.writerow({'groep': g, 'score': s, 'multiplier': multiplier[g]})
        except:
            print('Updating next iteration...')

    def read_scores_file(self):
        try:
            with open('scores.csv', 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                lines = list(reader)

        except:
            print('Updating next iteration...')
        return lines
