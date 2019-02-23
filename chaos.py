#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from barkas import Barkas
import numpy as np
import random
import json
import math
import threading
import time
import urllib.request
import queue

DATUM = datetime.date(2019,2,25)
GROEPERINGEN = ['Nobel', 'Krat', 'Bestuur 122', 'Spetter', 'Quast', 'Octopus', 'McClan', 'Kurk', 'Apollo', 'Schranz', 'Asene', 'Kielzog', 'Scorpios', 'Fabula', 'TDC 66']
CONSUMPTIES = ['Fris', 'Pul fris', 'Pul bier', 'Pitcher bier', 'Safari', 'Goldstrike', 'Amaretto Disaronno', 'Apfelkorn', 'Jaegermeister', 'Likeur 43', 'De Kuyper Peachtree']
S50 = ['Rum Bacardi Razz', 'Mede honingwijn']
multiplier = {}
SCORES = {}
SERVERURL = 'https://borrel.collegechaos.nl:2003'

#map from chaos to others
PRODUCT_MAP = {
    'Bier'          : 'Bier',
    #'Pul bier'      :
}

class Chaos:
    LATEST_CHECK_MINUTES = 0
    LATEST_CHECK_MINUTES_MULT = 0

    def __init__(self):
        for g in GROEPERINGEN:
            SCORES[g] = 0

        self.randomize_multipliers()
        self.chaos_orders = []

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

    def update_score(self, new_order):
        if self.check_if_update_mults():
            self.randomize_multipliers()
            print(multiplier)

        group = new_order['group']

        #if g not in SCORES:
        #    SCORES[g] = 0

        for c_order in self.chaos_orders:
            ts_diff_ms = new_order['timestamp'] - c_order['timestamp']
            if ts_diff_ms / 1000 > 1800:
                continue
            if self.product_matches(new_order['product'], c_order['product']):
                # TODO: product value multiplier
                SCORES[group] += round(10 * multiplier[group] * self.calc_amount_score(new_order['amount'], c_order['amount']))

    def send_current_state(self):
        try:
            senddata = {
                'scores' : [{'group':g, 'score':s, 'multiplier':multiplier[g]} for g,s in SCORES.items()],
            }
            urllib.request.urlopen(SERVERURL, json.dumps(senddata).encode())
        except Exception as e:
            print('Failed to update server because {}'.format(e))

    def trim_chaos_orders(self, trim_to):
        pre_len = len(self.chaos_orders)
        self.chaos_orders = [order for order in self.chaos_orders if (order['timestamp'] / 1000) >= trim_to]
        post_len = len(self.chaos_orders)
        print("Trimmed {}/{} chaos orders".format(pre_len - post_len, pre_len))

    def product_matches(self, group_product, chaos_product):
        try:
            return PRODUCT_MAP[chaos_product] == group_product
        except:
            return False

    def calc_amount_score(self, group_amount, chaos_amount):
        return math.log(1 + group_amount) * math.log(1 + chaos_amount)

    def mainloop(self, in_queue):
        next_send = 0
        next_trim = 0
        order = None
        order_timestamp = 0
        while True:
            try:
                order = in_queue.get_nowait()
                new_order = True
                order_timestamp = order['timestamp'] / 1000
                #print("Found new order")
            except queue.Empty:
                new_order = False

            if new_order:
                if order['group'] == 'Chaos':
                    self.chaos_orders.append(order)
                    print("Chaos order {}x {}".format(order['amount'], order['product']))
                elif order['group'] in GROEPERINGEN:
                    self.update_score(order)
                    print("Score updated for {} to {} for ordering {}x {}".format(order['group'], SCORES[order['group']], order['amount'], order['product']))
                else:
                    print("Ignoring {}".format(order['group']))

            if next_send <= time.time() or new_order and in_queue.empty():
                self.send_current_state()
                next_send = time.time() + 5
                print("sent scores: {}".format(SCORES))

            if next_trim <= time.time():
                self.trim_chaos_orders(order_timestamp - 1800)
                next_trim = time.time() + 300

            earliest_event = min((next_send, ))
            time_to_event = earliest_event - time.time()
            max_sleep = 5 if not new_order else 0
            min_sleep = 0
            time.sleep(max(min_sleep, min(max_sleep, time_to_event)))
            #print("Iter done")

class BarkasProducer(threading.Thread):
    def __init__(self, date_bon, out_queue):
        super(BarkasProducer, self).__init__()
        print("Producer inited")
        self.running = True
        self.barkas = Barkas()
        self.date_bon = date_bon
        self.out_queue = out_queue
    def run(self):
        stream = self.barkas.get_orders_of_day_stream(self.date_bon)
        print("Producer started")
        num = 0
        t = time.time()
        while self.running:
            self.out_queue.put(next(stream))
            num += 1
            if num % 10 == 0 and num / 10 > time.time() - t:
                time.sleep(5)
                t = time.time()
        print("Producer stopping")

def main():
    print('Running')
    q = queue.Queue(10)

    barkas_producer = BarkasProducer(DATUM, q)
    app = Chaos()

    barkas_producer.start()
    try:
        app.mainloop(q)
    finally:
        barkas_producer.running = False
        barkas_producer.join()

if __name__ == '__main__':
    main()  
