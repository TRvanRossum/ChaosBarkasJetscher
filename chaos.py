#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from barkas import Barkas
from tkinter import Tk, Frame, BOTH, Label, StringVar, CENTER
import numpy as np

DATUM = "2015-11-06"
DRANK = "Bier zwembadfeest"
GROEPERINGEN = ['Nobel', 'Krat', 'Bestuur 122', 'Spetter', 'Quast', 'Octopus', 'McClan', 'Kurk', 'Apollo', 'Schranz', 'Asene', 'Kielzog', 'Scorpios', 'Fabula', 'TDC 66']
CONSUMPTIES = ['Fris', 'Pul Fris', 'Safari', 'Apfelkorn', 'Eristoff', 'Jagermeister', 'Likeur 43', 'Pitcher bier', 'Peach Tree']
S50 = ['bacardi razz', 'honingwijn']
SCORES = {}
BESTELLINGEN = {}

class Example(Frame):

    MAP_CONS = {}
    MAP_S50 = {}
    LATEST_CHECK_MINUTES = 0

    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")   
         
        self.parent = parent
        

        self.names = {}
        self.scores = {}
        for i, g in enumerate(GROEPERINGEN):
            self.names[i] = StringVar()
            self.scores[i] = StringVar()

        for g in GROEPERINGEN:
            BESTELLINGEN[g] = self.get_null_order()
            SCORES[g] = 0.0

        self.initUI()
        self.MAP_CONS = self.create_random_mapping(CONSUMPTIES)
        self.MAP_S50 = self.create_random_mapping(S50)
        self.update_scores_test()
        #self.update_scores()

    def get_null_order(self):
        res = {}
        res['Bier'] = 0
        for n in CONSUMPTIES:
            res[n] = 0
        for n in S50:
            res[n] = 0
        return res

    def initUI(self):
        self.parent.title("Scores")
        w = Label(self, textvariable="Running", font=("Helvetica", 15))


    def get_total_orders_of_group(self, group):
        self.barkas = Barkas()

        date = datetime.date.today()
        orders = {}
        for name in CONSUMPTIES:
            orders[name] = self.barkas.get_number_of_consumptions(date, group, name)

        for name in S50:
            orders[name] = self.barkas.get_number_of_s50(date, group, name)

        orders['Bier'] = self.barkas.get_number_of_beers(date, group)

        return orders

    def normalize_orders(self, order):
        res = {}
        sum = 0
        for n, v in order.items():
            sum += v
        if sum == 0:
            return order
        for n, v in order.items():
            res[n] = float(v)/float(sum)

        # Pad order. Add a quantity of 0 for every item not yet in
        # the normalized order that is defined in CONSUMPTIES, S50 or just beer.
        for n in CONSUMPTIES:
            if not(n in res):
                res[n] = 0

        for n in S50:
            if not(n in res):
                res[n] = 0

        if not('Bier' in res):
            res['Bier'] = 0

        return res

    def compare_old_and_new_orders(self, old, new):
        changed = False
        new_order = {}
        for n, v in new.items():
            if v > old.get(n, 0):
                changed = True
            new_order[n] = new[n] - old.get(n, 0)

        return (changed, new_order)

    # Calculates score of an order based on Chi-square distance with what Chaos has ordered.
    # This method complicated the scoring procedure so I decided to create a simpler method.
    def chi_square_sim(self, orders_Chaos, orders_other):
        dist = 0
        for name, val in orders_Chaos.items():
            if val > 0:
                dist += (float((val - orders_other[name])**2)/float(val))

        # Return 15.0 minus the distance. This is very hacky, but it awards more points for orders very close to us.
        return 15.0 - dist

    # Far simpler way to calculate scores. The score for an order is calculated by
    # using the function min(the amount of X Chaos has ordered total, the amount of X in the other order),
    # and then summing that for all items.
    def calculate_extra_score(self, orders_Chaos, orders_other):
        score = 0
        for name, val in orders_Chaos.items():
            score += min(val, orders_other[name])
        return score

    # These two functions are for the creation of random mappings. Consumptions are mapped to consumptions
    # and S50 is mapped to S50. Beer is not mapped to anything else.
    def create_random_mappings(self):
        map_cons = self.create_random_mapping(CONSUMPTIES)
        map_s50 = self.create_random_mapping(S50)
        return (map_cons, map_s50)

    def create_random_mapping(self, input):
        map_from = input
        map_to = np.random.permutation(map_from)
        res = {}
        for i in range(len(map_from)):
            res[map_from[i]] = map_to[i]
        return res

    def randomize_orders(self, orders):
        res = {}

        # Do not remap beer.
        res['Bier'] = orders['Bier']

        # If an order contains X of item A and item A is mapped to item B, then the randomized order contains X amount of item B.
        for k, v in self.MAP_CONS.items():
            if k in orders:
                res[v] = orders[k]
            else:
                res[v] = 0

        # Same, but for S50.
        for k, v in self.MAP_S50.items():
            if k in orders:
                res[v] = orders[k]
            else:
                res[v] = 0

        return res



    # The random maps need to be re-randomized every 30 minutes. This function checks if 30 minutes have passed already.
    def check_if_maps_need_updating(self):
        current_time = datetime.datetime.now()
        current_time_mins = current_time.minute

        # If 30 minutes have passed, the min_mod_30 variable should be less than the previous one.
        checked = False
        min_mod_30 = current_time_mins % 30
        if min_mod_30 < self.LATEST_CHECK_MINUTES:
            checked = True

        self.LATEST_CHECK_MINUTES = min_mod_30
        return checked


    def update_scores(self):
        print("Update")

        # Check if randomized maps need updating.
        if self.check_if_maps_need_updating():
            (map_c, map_s) = self.create_random_mappings()
            self.MAP_CONS = map_c
            self.MAP_S50 = map_s

        # Get orders of Chaos
        orders_Chaos = self.get_total_orders_of_group('Chaos')

        # For every group, check if a new order has been made.
        # If so, compare this to what Chaos has ordered.
        for g in GROEPERINGEN:
            g_orders_old = BESTELLINGEN[g]
            g_orders_new = self.get_total_orders_of_group(g)
            (changed, new_orders) = self.compare_old_and_new_orders(g_orders_old, g_orders_new)
            # If a new order has been placed by a group, update the score of that group.
            if changed:
                # Randomize the new order of that group, and then compare it with what Chaos has ordered.
                random_orders = self.randomize_orders(new_orders)
                # score = self.chi_square_sim(self.normalize_orders(orders_Chaos), self.normalize_orders(random_orders))
                score = self.calculate_extra_score(self.normalize_orders(orders_Chaos), self.normalize_orders(random_orders))
                SCORES[g] += score

        print(SCORES)

        # Keep running this function every 10 seconds.
        self.after(10000, self.update_scores)

    def update_scores_test(self):
        print("Update")
        print(SCORES)
        SCORES['Krat'] += 1.0
        self.check_if_maps_need_updating()
        print(self.LATEST_CHECK_MINUTES)
        (i, j) = self.create_random_mappings()
        print(i)
        print(j)
        self.MAP_CONS = i
        self.MAP_S50 = j
        o = self.get_null_order()
        o['Bier'] = 5
        o['Fris'] = 3
        o['Pul Fris'] = 1
        print(o)
        o2 = self.randomize_orders(o)
        print('Test for randomization of orders...')
        print(o2)
        self.after(15000, self.update_scores_test)
        

def main():
  
    root = Tk()
    root.geometry("800x500")
    print('Running')
    app = Example(root)
    root.mainloop()  


    #     time.sleep(1)



if __name__ == '__main__':
    main()  
