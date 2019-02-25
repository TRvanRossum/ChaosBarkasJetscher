#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from barkas import Barkas
import hashlib
import json
import math
import queue
import random
import threading
import time
import sys
import urllib.request

# For random.choices
from bisect import bisect as _bisect
from itertools import accumulate as _accumulate, repeat as _repeat

DATUM = datetime.date(2019,2,25)
GROEPERINGEN = ['Nobel', 'Krat', 'Bestuur 122', 'Spetter', 'Quast', 'Octopus', 'McClan', 'Kurk', 'Apollo', 'Schranz', 'Asene', 'Kielzog', 'Scorpios', 'Fabula', 'TDC 66']
SERVERURL = 'https://borrel.collegechaos.nl:2003'

#map from chaos to others
PRODUCT_MAP = {
    'Bier'                      : 'Bier',
    'Fris'                      : 'Fris',
    'Meter bier'                : 'Meter bier',
    'Pitcher bier'              : 'Jenever Hooghoudt Dubbele',
    'Jenever Ketel 1 Jonge'     : 'Likeur 43',
    'Jenever Hooghoudt Dubbele' : 'Safari',
    'Rum Havana Club'           : 'Amaretto Disaronno',
    'Rum Bacardi'               : 'Whisky Talisker',
    'Wodka Puschkin'            : 'De Kuyper Peachtree',
    'Whisky Talisker'           : 'Apfelkorn',
    'Goldstrike'                : 'Jaegermeister',
    'Amaretto Disaronno'        : 'Goldstrike',
    'Safari'                    : 'Safari',
    'Dropshot'                  : 'Rum Havana Club',
    'Coebergh Rood Fruit'       : 'Rum Bacardi',
    'Likeur 43'                 : 'Jenever Ketel 1 Jonge',
    'Apfelkorn'                 : 'Pitcher bier',
    'De Kuyper Peachtree'       : 'Dropshot',
    'Jaegermeister'             : 'Wodka Puschkin',
}
MAP_FOLD = {
    'Pul bier'                  : 'Bier',
    'Pul bier met korting'      : 'Bier',
    'Pul fris'                  : 'Fris',
    'Jenever Hooghoudt Vieux'   : 'Jenever Hooghoudt Dubbele',
    'Jenever Hooghoudt Premium' : 'Jenever Hooghoudt Dubbele',
    'Rum Bacardi Limon'         : 'Rum Bacardi',
    'Rum Bacardi Razz'          : 'Rum Bacardi',
    'Wodka Puschkin Red'        : 'Wodka Puschkin',
    'Puschkin Whipped Cream'    : 'Wodka Puschkin',
}
PRODUCT_VALUE = {
    'Bier'                      : 1,
    'Pul bier'                  : 3,
    'Pul bier met korting'      : 3,
    'Fris'                      : 1,
    'Pul fris'                  : 3,
    'Meter bier'                : 10,
    'Pitcher bier'              : 10,
    'Jenever Ketel 1 Jonge'     : 5,
    'Jenever Hooghoudt Dubbele' : 5,
    'Jenever Hooghoudt Vieux'   : 5,
    'Jenever Hooghoudt Premium' : 7,
    'Rum Havana Club'           : 7,
    'Rum Bacardi'               : 5,
    'Rum Bacardi Limon'         : 5,
    'Rum Bacardi Razz'          : 5,
    'Wodka Puschkin'            : 5,
    'Wodka Puschkin Red'        : 5,
    'Puschkin Whipped Cream'    : 5,
    'Whisky Talisker'           : 10,
    'Goldstrike'                : 8,
    'Amaretto Disaronno'        : 5,
    'Safari'                    : 5,
    'Dropshot'                  : 5,
    'Coebergh Rood Fruit'       : 5,
    'Rum Bacardi'               : 5,
    'Likeur 43'                 : 6,
    'Apfelkorn'                 : 5,
    'De Kuyper Peachtree'       : 5,
    'Jaegermeister'             : 7,
}
BLUE_SHELL_PRODUCTS = {
    (20, 00) : 'Amaretto Disaronno',
    (20, 30) : 'Wodka Puschkin',
    (21, 00) : 'Jenever Ketel 1 Jonge',
    (21, 30) : 'Jaegermeister',
    (22, 00) : 'Goldstrike',
    (22, 30) : 'Jenever Hooghoudt Dubbele',
}
SECONDS_BETWEEN_BUMPS = 900
MAX_SECONDS_BETWEEN_ORDERS = 1800
DECAY_INTERVAL = 10
BLUE_SHELL_DECAY_INTERVAL = 1200
MSG_TIME_ORBIT = 300

# Lifted from python 3.6+
class BetterRandom(random.Random):
    def choices(self, population, weights=None, *, cum_weights=None, k=1):
        """Return a k sized list of population elements chosen with replacement.
        If the relative weights or cumulative weights are not specified,
        the selections are made with equal probability.
        """
        random = self.random
        n = len(population)
        if cum_weights is None:
            if weights is None:
                _int = int
                n += 0.0    # convert to float for a small speed improvement
                return [population[_int(random() * n)] for i in _repeat(None, k)]
            cum_weights = list(_accumulate(weights))
        elif weights is not None:
            raise TypeError('Cannot specify both weights and cumulative weights')
        if len(cum_weights) != n:
            raise ValueError('The number of weights does not match the population')
        bisect = _bisect
        total = cum_weights[-1] + 0.0   # convert to float
        hi = n - 1
        return [population[bisect(cum_weights, random() * total, 0, hi)]
                for i in _repeat(None, k)]

class Chaos:
    LATEST_CHECK_MINUTES = 0
    LATEST_CHECK_MINUTES_MULT = 0

    def __init__(self, run_date):
        self.chaos_orders = []
        self.scores = {}
        self.electron_shells = [[None, None], [], []]
        self.next_electron_bump = 0
        self.next_electron_infall = 0
        self.multipliers = {}
        self.messages = []
        self.blue_shells_fired = {}
        # TODO: start time
        #self.messages.append({
        #    "message":
        #})
        self.messages.extend({
            "message":"{} is nu radioactief! Bestel het als je zelf dichter bij de kern wil komen.".format(prod),
            "from":run_date.replace(hour=hour,minute=minute,second=0,microsecond=0).timestamp(),
            "to":(run_date.replace(hour=hour,minute=minute,second=0,microsecond=0)+datetime.timedelta(minutes=30)).timestamp()
        } for (hour, minute), prod in BLUE_SHELL_PRODUCTS.items())
        # TODO: end!

    def update_score(self, new_order):
        group = new_order['group']

        if group not in GROEPERINGEN:
            return
        if group not in self.scores:
            self.scores[group] = 0
        if group not in self.multipliers:
            self.multipliers[group] = 1

        for c_order in self.chaos_orders:
            ts_diff_ms = new_order['timestamp'] - c_order['timestamp']
            if ts_diff_ms / 1000 > MAX_SECONDS_BETWEEN_ORDERS:
                continue
            if self.product_matches(new_order['product'], c_order['product']):
                # TODO: time difference multiplier
                self.scores[group] += round(10 * self.multipliers[group] * PRODUCT_VALUE[new_order['product']] * self.calc_amount_score(new_order['amount'], c_order['amount']))

    def send_current_state(self):
        try:
            self.messages = [msg for msg in self.messages if msg['to'] > time.time()]
            senddata = {
                'scores' : [{'group':g, 'score':s, 'multiplier':self.multipliers[g]} for g,s in self.scores.items()],
                'electrons' : self.electron_shells,
                'messages' : self.messages,
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
        if group_product in MAP_FOLD:
            group_product = MAP_FOLD[group_product]
        if chaos_product in MAP_FOLD:
            chaos_product = MAP_FOLD[chaos_product]

        if chaos_product in PRODUCT_MAP:
            return PRODUCT_MAP[chaos_product] == group_product

        return False

    def calc_amount_score(self, group_amount, chaos_amount):
        return math.log(1 + group_amount) * math.log(1 + chaos_amount)

    # The idea is:
    # Up to 2 groups: (x, 0, 0)
    # Up to 4 groups: (2, x-2, 0)
    # Up to 7 groups: (2, x-3, 1)
    # Up to 12 groups: (2, x-4, 2)
    # Above: (2, 8, x-10)
    # However, we do want to have empty spots to kick people up to
    def maybe_update_orbits(self, order):
        num_groups = len(self.scores)

        # Maybe expand number of orbits
        num_orbits = sum(len(shell) for shell in self.electron_shells)
        if num_groups + 2 >= num_orbits:
            # Need to expand shells
            if num_groups > 11:
                wanted_centers = 8
            elif num_groups > 4:
                wanted_centers = num_groups - 2
            else:
                wanted_centers = 2
            while len(self.electron_shells[0]) < 2:
                self.electron_shells[0].append(None)
            while len(self.electron_shells[1]) < wanted_centers:
                self.electron_shells[1].append(None)

            needed_outers = num_groups - len(self.electron_shells[0]) - len(self.electron_shells[1]) + 2
            wanted_outers = 4*(math.ceil(needed_outers / 4))
            while len(self.electron_shells[2]) < wanted_outers:
                self.electron_shells[2].append(None)

        # Drop in group if it did not have a location yet (outermost orbit with spots)
        if order['group'] in GROEPERINGEN and all(order['group'] not in orbit for orbit in self.electron_shells):
            try:
                target_shell = next(ix for ix, orbit in enumerate(self.electron_shells) if any(group is None for group in orbit))
            except StopIteration:
                target_shell = 2
                self.electron_shells[target_shell].append(None)
            empty_spot = next(ix for ix, group in enumerate(self.electron_shells[target_shell]) if group is None)
            self.electron_shells[target_shell][empty_spot] = order['group']
            self.messages.append({
                'message': "{} TODO translate has joined!".format(order['group']),
                'from': order['timestamp'] / 1000,
                'to': order['timestamp'] / 1000 + MSG_TIME_ORBIT,
            })

        # Maybe kick out one of the center ones
        do_bump = False
        if self.next_electron_bump <= order['timestamp'] / 1000:
            do_bump = True
            self.next_electron_bump = (order['timestamp'] / 1000) + SECONDS_BETWEEN_BUMPS
        if not do_bump and self.is_blue_shell(order):
            do_bump = True
            self.messages.append({
                'message': "{} heeft een radioactieve bestelling gedaan! Hun volgende bestelling moet voorlopig tenminste {} groot zijn.".format(order['group'], self.blue_shells_fired[group]['amount']),
                'from': order['timestamp'],
                'to': self.blue_shells_fired[group]['timeout'],
            })

        if do_bump:
            rand = random.Random()
            rand.seed(order['timestamp'])
            if self.electron_shells[0][0] is None and self.electron_shells[0][1] is not None:
                bump_index = 1
            elif self.electron_shells[0][0] is not None and self.electron_shells[0][1] is None:
                bump_index = 0
            elif all(x is None for x in self.electron_shells[0]):
                return
            else:
                bump_index = rand.randint(0,1)

            target_shell = 2 if len(self.electron_shells[2]) > 0 or all(group is not None for group in self.electron_shells[1]) else 1
            try:
                empty_spot = next(ix for ix, group in enumerate(self.electron_shells[target_shell]) if group is None)
            except StopIteration:
                target_shell = 2
                empty_spot = len(self.electron_shells[2])
                self.electron_shells.append(None)
            bumped_group = self.electron_shells[0][bump_index]
            self.electron_shells[target_shell][empty_spot] = bumped_group
            self.electron_shells[0][bump_index] = None
            self.update_multiplier(bumped_group, target_shell)
            self.messages.append({
                'message': "{} is uit de binnenste baan gegooid!".format(bumped_group),
                'from': order['timestamp'] / 1000,
                'to': order['timestamp'] / 1000 + MSG_TIME_ORBIT,
            })

        return do_bump

    def do_infall(self):
        empty_shell = next(ix for ix, orbit in enumerate(self.electron_shells) if any(group is None for group in orbit))
        empty_ix = next(ix for ix, group in enumerate(self.electron_shells[empty_shell]) if group is None)
        filled_shell = next((empty_shell+1+ix for ix, orbit in enumerate(self.electron_shells[empty_shell+1:]) if any(group is not None for group in orbit)), None)

        # This check should always return true, but let's make sure
        if filled_shell is not None:
            candidates = [(ix, group) for ix, group in enumerate(self.electron_shells[filled_shell]) if group is not None]
            rand = BetterRandom()
            # Hashing current config + scores for seed. Hopefully that's deterministic enough
            hasher = hashlib.sha256()
            hasher.update(json.dumps(self.electron_shells).encode())
            hasher.update(json.dumps(self.scores).encode())
            rand.seed(hasher.digest())
            # Weight on scores
            avg_score = sum(self.scores[group]/len(candidates) for group in candidates)
            weights = [max(5, min(15, 10+10*(avg_score - self.scores[group])/avg_score )) for group in candidates]
            #TODO: priority for blue shellers
            windex, winner = rand.choices(candidates)[0]
            self.electron_shells[empty_shell][empty_ix] = winner
            self.electron_shells[filled_shell][windex] = None
            self.update_multiplier(winner, empty_shell)
            self.messages.append({
                'message': "{} heeft een {} gevonden".format(winner, "plek in de binnenste baan" if empty_shell == 0 else "betere plek"),
                'from': time.time(),
                'to': time.time() / 1000 + MSG_TIME_ORBIT,
            })

        # Check if there's another empty spot below a shell with electrons
        empty_shell = next((ix for ix, orbit in enumerate(self.electron_shells) if any(group is None for group in orbit)), None)
        filled_shell = next((empty_shell+1+ix for ix, orbit in enumerate(self.electron_shells[empty_shell+1:]) if any(group is not None for group in orbit)), None) if empty_shell is not None else None

        # Whether a new infall should be scheduled
        return empty_shell is not None and filled_shell is not None

    def update_multiplier(self, group, new_shell):
        self.multipliers[group] = (4 if new_shell == 0 else (2 if new_shell == 1 else 1))

    def is_blue_shell(self, order):
        ts = order['timestamp'] / 1000
        dt = datetime.datetime.fromtimestamp(ts)
        prod = order['product']
        group = order['group']
        shell_prod = next((product for (hour, minute), product in BLUE_SHELL_PRODUCTS.items() if (dt.hour > hour) or (dt.hour == hour and dt.minute >= minute)), None)
        if prod != shell_prod:
            return False
        if group not in self.blue_shells_fired or self.blue_shells_fired[group]['timeout'] < ts:
            self.blue_shells_fired[group] = {
                'timeout' : ts + BLUE_SHELL_DECAY_INTERVAL,
                'amount' : 3,
            }
            return True
        if order['amount'] >= self.blue_shells_fired[group]['amount']:
            self.blue_shells_fired[group]['timeout'] = ts + BLUE_SHELL_INTERVAL
            self.blue_shells_fired[group]['amount'] *= 3
            return True
        return False

    def mainloop(self, in_queue):
        last_send = 0
        next_send = 0
        next_trim = 0
        order = None
        order_timestamp = 0
        next_infall_order = None
        next_infall_time = None
        while True:
            try:
                order = in_queue.get_nowait()
                new_order = True
                order_timestamp = order['timestamp'] / 1000
                #print("Found new order")
            except queue.Empty:
                new_order = False

            if new_order and self.maybe_update_orbits(order):
                next_infall_order = order_timestamp + DECAY_INTERVAL
                next_infall_time = time.time() + DECAY_INTERVAL*2

            # We want to do an infall DECAY_INTERVAL seconds after an empty space is formed.
            # We would like to make sure all orders in that interval have been processed,
            # as that would make us deterministic.
            # Somewhat safe alternative condition: two times the interval has passed in real time?
            if next_infall_order is not None and (next_infall_order < order_timestamp or next_infall_time < time.time()):
                if self.do_infall():
                    # Unsure about determinism here
                    next_infall_order = order_timestamp + DECAY_INTERVAL
                    next_infall_time = time.time() + DECAY_INTERVAL*2
                else:
                    next_infall_order = None
                    next_infall_time = None

            if new_order:
                if order['group'] == 'Chaos':
                    self.chaos_orders.append(order)
                    print("Chaos order {}x {}".format(order['amount'], order['product']))
                    self.messages.append({
                        'message': "Chaos heeft {} besteld.".format(order['product']),
                        'from': order['timestamp'] / 1000 + 300,
                        'to': order['timestamp'] / 1000 + MAX_SECONDS_BETWEEN_ORDERS,
                    })
                elif order['group'] in GROEPERINGEN:
                    self.update_score(order)
                    print("Score updated for {} to {} for ordering {}x {}".format(order['group'], self.scores[order['group']], order['amount'], order['product']))
                else:
                    print("Ignoring {}".format(order['group']))

            if next_send <= time.time() or (new_order and in_queue.empty() and last_send + 1 <= time.time()):
                self.send_current_state()
                last_send = time.time()
                next_send = time.time() + 5
                print("sent scores: {}".format(self.scores))

            if next_trim <= time.time():
                self.trim_chaos_orders(order_timestamp - MAX_SECONDS_BETWEEN_ORDERS)
                next_trim = time.time() + 300

            earliest_event = min((next_send, ))
            time_to_event = earliest_event - time.time()
            max_sleep = 5 if not new_order else 0
            min_sleep = 0
            time.sleep(max(min_sleep, min(max_sleep, time_to_event)))
            #print("Iter done")

class BarkasProducer(threading.Thread):
    def __init__(self, date_bon, out_queue, delay):
        super(BarkasProducer, self).__init__()
        print("Producer inited")
        self.running = True
        self.barkas = Barkas()
        self.date_bon = date_bon
        self.out_queue = out_queue
        self.delay = delay
    def run(self):
        stream = self.barkas.get_orders_of_day_stream(self.date_bon)
        print("Producer started")
        num = 0
        t = time.time()
        while self.running:
            self.out_queue.put(next(stream))
            num += 1
            if self.delay and num % 10 == 0 and num / 10 > time.time() - t:
                time.sleep(5)
                t = time.time()
        print("Producer stopping")

def main():
    q = queue.Queue(10)

    try:
        str_date = next(arg.split('=')[1] for arg in sys.argv if arg.startswith("--date="))
        run_date = datetime.date(*[int(part.lstrip('0')) for part in str_date.split('-')])
    except Exception as e:
        run_date = DATUM

    print('Running on {}'.format(run_date))

    delay = "--delay" in sys.argv
    barkas_producer = BarkasProducer(run_date, q, delay=delay)
    app = Chaos(run_date)

    barkas_producer.start()
    try:
        app.mainloop(q)
    finally:
        barkas_producer.running = False
        barkas_producer.join()

if __name__ == '__main__':
    main()  
