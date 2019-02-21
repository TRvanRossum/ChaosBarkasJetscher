#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from barkas import Barkas
from tkinter import Tk, Frame, BOTH, Label, StringVar, CENTER
import numpy as np
import random
import csv
import json
import urllib.request

DATUM = "2015-11-06"
DRANK = "Bier zwembadfeest"
GROEPERINGEN = ['Nobel', 'Krat', 'Bestuur 122', 'Spetter', 'Quast', 'Octopus', 'McClan', 'Kurk', 'Apollo', 'Schranz', 'Asene', 'Kielzog', 'Scorpios', 'Fabula', 'TDC 66']
CONSUMPTIES = ['Fris', 'Pul fris', 'Pul bier', 'Pitcher bier', 'Safari', 'Goldstrike', 'Amaretto Disaronno', 'Apfelkorn', 'Jaegermeister', 'Likeur 43', 'De Kuyper Peachtree']
S50 = ['Rum Bacardi Razz', 'Mede honingwijn']
multiplier = {}
SCORES = {}
BESTELLINGEN = {}
SERVERURL = 'http://borrel.collegechaos.nl'

class Example(Frame):

    barkas = None
    MAP_CONS = {}
    MAP_S50 = {}
    LATEST_CHECK_MINUTES = 0
    LATEST_CHECK_MINUTES_MULT = 0

    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")   
         
        self.parent = parent

        for g in GROEPERINGEN:
            BESTELLINGEN[g] = self.get_null_order()
            SCORES[g] = 0

        self.names = {}
        self.scores = {}
        for i, g in enumerate(GROEPERINGEN):
            self.names[i] = StringVar()
            self.scores[i] = StringVar()

        self.initUI()
        self.MAP_CONS = self.create_random_mapping(CONSUMPTIES)
        self.MAP_S50 = self.create_random_mapping(S50)
        self.randomize_multipliers()
        #self.update_scores_test()
        self.update_scores()

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
        for i, g in enumerate(GROEPERINGEN):
            print(g)
            w = Label(self, text=str(g), font=("Helvetica", 15))
            w.place(rely=0.95 * i / float(len(GROEPERINGEN)) + 0.05, relx=0.3, anchor=CENTER)
            self.names[i].set(g)

            w = Label(self, textvariable=self.scores[i], font=("Helvetica", 15))
            w.place(rely=0.95 * i / float(len(GROEPERINGEN)) + 0.05, relx=0.6, anchor=CENTER)
            self.scores[i].set(str(SCORES.get(g, 0)))

        self.pack(fill=BOTH, expand=1)

    def get_total_orders_of_group(self, group):

        date = datetime.date.today()
        orders = {}
        for name in CONSUMPTIES:
            orders[name] = int(self.barkas.get_number_of_consumptions(date, group, name))

        for name in S50:
            orders[name] = int(self.barkas.get_number_of_s50(date, group, name))

        orders['Bier'] = int(self.barkas.get_number_of_beers(date, group))

        return orders

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
            score += min(val, orders_other.get(name, 0))
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

    def randomize_multipliers(self):
        rand_groups = np.random.permutation(GROEPERINGEN)
        for i in range(3):
            multiplier[rand_groups[i]] = 3
        for i in range(3, 8):
            multiplier[rand_groups[i]] = 2
        for i in range(8, len(GROEPERINGEN)):
            multiplier[rand_groups[i]] = 1

    def check_if_update_mults(self):
        current_time = datetime.datetime.now()
        current_time_mins = current_time.minute

        # If 10 minutes have passed, the min_mod_100 variable should be less than the previous one.
        checked = False
        min_mod_10 = current_time_mins % 10
        if min_mod_10 < self.LATEST_CHECK_MINUTES_MULT:
            checked = True

        self.LATEST_CHECK_MINUTES_MULT = min_mod_10
        return checked

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

    def update_scores_local(self):
        for i, g in enumerate(GROEPERINGEN):
            self.scores[i].set(SCORES.get(g, 0))

    def update_scores(self):
        self.barkas = Barkas()
        # Check if randomized maps need updating.
        if self.check_if_maps_need_updating():
            (map_c, map_s) = self.create_random_mappings()
            self.MAP_CONS = map_c
            self.MAP_S50 = map_s

        self.randomize_multipliers()

        if self.check_if_update_mults():
            self.randomize_multipliers()

        print(multiplier)

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
                # Update the amount of ordered things.
                BESTELLINGEN[g] = g_orders_new
                # Randomize the new order of that group, and then compare it with what Chaos has ordered.
                score = multiplier[g] * self.calculate_extra_score(orders_Chaos, new_orders)
                SCORES[g] += score
        print('Scores this iteration:')
        print(SCORES)
        print('Orders this iteration:')
        print(BESTELLINGEN)

        try:
            senddata = {
                'scores' : [{'group':g, 'score':s, 'multiplier':multiplier[g]} for g,s in SCORES.items()],
            }
            urllib.request.urlopen(SERVERURL, json.dumps(senddata).encode())
        except:
            print('Updating next iteration...')

        # Keep running this function every 10 seconds.
        self.after(500, self.update_scores)

    def update_scores_test(self):
        (i, j) = self.create_random_mappings()
        self.MAP_CONS = i
        self.MAP_S50 = j
        o = self.get_null_order()
        o['Bier'] = 5
        o['Fris'] = 3
        o['Pul fris'] = 1
        #print('Orders')
        #print(o)
        o2 = self.randomize_orders(o)
        #print('Orders Randomized')
        #print(o2)

        chaos = self.get_null_order()
        chaos['Bier'] = 5
        chaos['Pitcher bier'] = 3
        chaos['Safari'] = 1
        score = self.calculate_extra_score(chaos, o2)
        o_new = self.get_null_order()
        o_new['Bier'] = 8
        o_new['Fris'] = 4
        o_new['Pul fris'] = 2
        (_, b) = self.compare_old_and_new_orders(o, o_new)
        o_new_2 = self.randomize_orders(b)
        print(o_new_2)
        extra_score = self.calculate_extra_score(chaos, o_new_2)
        print(extra_score)
        group = random.choice(GROEPERINGEN)
        SCORES[group] += score
        self.update_scores_local()
        self.after(3000, self.update_scores_test)
        

def main():
  
    root = Tk()
    root.geometry("800x500")
    print('Running')
    app = Example(root)
    root.mainloop()  


    #     time.sleep(1)



if __name__ == '__main__':
    main()  
