import csv

class Logger:

    scores_file = ''
    orders_file = ''

    def __init__(self, _scores_f, _orders_f):
        self.scores_file = _scores_f
        self.orders_file = _orders_f

    def write_scores_file(self, scores, multiplier):
        try:
            with open(self.scores_file, 'w', newline='') as csvfile:
                fieldnames = ['groep', 'score', 'multiplier']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for g, s in scores.items():
                    writer.writerow({'groep': g, 'score': s, 'multiplier': multiplier[g]})
        except:
            print('Updating next iteration...')

    def read_scores_file(self):
        try:
            with open(self.scores_file, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                lines = list(reader)

        except:
            print('Updating next iteration...')
        res = {}
        mults = {}
        for i in range(1, len(lines)):
            row = lines[i]
            group = row[0]
            score = int(row[1])
            mult = int(row[2])
            res[group] = score
            mults[group] = mult
        return (res, mults)

    def write_orders_file(self, orders, cons, s50):
        list = ['groep']
        list.append('Bier')
        for i in cons:
            list.append(i)
        for i in s50:
            list.append(i)

        try:
            with open(self.orders_file, 'w', newline='') as csvfile:
                fieldnames = list
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for g, o in orders.items():
                    row = {}
                    row['groep'] = g
                    for i, a in o.items():
                        row[i] = a
                    writer.writerow(row)
        except:
            print('Updating next iteration...')

    def read_orders_file(self):
        try:
            with open(self.orders_file, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                lines = list(reader)

        except:
            print('Updating next iteration...')
        res = {}
        header = lines[0]
        for i in range(1, len(lines)):
            all_consumptions = lines[i]
            group = all_consumptions[0]
            foo = {}
            for j in range(1, len(all_consumptions)):
                foo[header[j]] = int(all_consumptions[j])
            res[group] = foo
        return res