#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from barkas import Barkas
from tkinter import Tk, Frame, BOTH, Label, StringVar, CENTER

DATUM = "2015-11-06"
DRANK = "Bier zwembadfeest"
GROEPERINGEN = ['Nobel', 'Krat', 'Bestuur 122', 'Spetter', 'Quast', 'Octopus', 'McClan', 'Kurk', 'Apollo', 'Schranz', 'Asene', 'Kielzog', 'Scorpios', 'Fabula', 'TDC 66']
CONSUMPTIES = ['Fris', 'Pul Fris', 'Safari', 'Apfelkorn', 'Eristoff', 'Jagermeister', 'Likeur 43', 'Pitcher bier', 'Peach Tree ']
S50 = ['bacardi razz', 'honingwijn']
SCORES = {}
BESTELLINGEN = {}

class Example(Frame):

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
        self.update_scores_test()
        #self.update_scores()

    def get_null_order(self):
        res = {'Fris': 0, 'Pul Fris': 0, 'Safari': 0, 'Apfelkorn': 0, 'Eristoff': 0, 'Jagermeister': 0, 'Likeur 43': 0, 'Pitcher bier': 0, 'Peach Tree ': 0, 'Bier': 0, 'bacardi razz': 0, 'honingwijn': 0}
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
        for n, v in order:
            sum += v
        if sum == 0:
            return order
        for n, v in order:
            res[n] = float(v)/float(sum)
        return res

    def compare_old_and_new_orders(self, old, new):
        changed = False
        new_order = {}
        for n, v in old:
            if v < new[n]:
                changed = True
            new_order[n] = new[n] - v

        return (changed, new_order)

    def chi_square_sim(self, orders_Chaos, orders_other):
        dist = 0
        for name, val in orders_Chaos:
            if val > 0:
                dist += (float((val - orders_other[name])**2)/float(val))

        # Return 15.0 minus the distance. This is very hacky, but it awards more points for orders very close to us.
        return 15.0 - dist


    def update_scores(self):
        print("Update")

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
                similarity = self.chi_square_sim(self.normalize_orders(orders_Chaos), self.normalize_orders(new_orders))
                SCORES[g] += similarity


        self.after(3000, self.update_scores)

    def update_scores_test(self):
        print("Update")
        print(SCORES)
        SCORES['Krat'] += 1.0
        self.after(1000, self.update_scores_test)
        

def main():
  
    root = Tk()
    root.geometry("800x500")
    print('Running')
    app = Example(root)
    root.mainloop()  


    #     time.sleep(1)



if __name__ == '__main__':
    main()  
