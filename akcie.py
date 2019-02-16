#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from barkas import Barkas
from bestellingen import Bestelling
from tkinter import Tk, Frame, BOTH, Label, StringVar, CENTER

DATUM = "2015-11-06"
DRANK = "Bier zwembadfeest"
GROEPERINGEN = ['Nobel', 'Krat', 'Bestuur 122', 'Chaos', 'Spetter', 'Quast', 'Octopus', 'McClan', 'Kurk', 'Apollo', 'Schranz', 'Asene', 'Kielzog', 'Scorpios', 'Fabula', 'TDC 66']
CONSUMPTIES = ['Fris', 'Pul Fris', 'Safari', 'Apfelkorn', 'Eristoff', 'Jagermeister', 'Likeur 43', 'Pitcher bier', 'Peach Tree ']
S50 = ['bacardi razz', 'honingwijn']
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
            BESTELLINGEN[g] = Bestelling(g)

        self.initUI()
        #self.update_scores()
    
    def initUI(self):
        self.parent.title("Scores")
        for i, g in enumerate(GROEPERINGEN):
            w = Label(self, textvariable=self.names[i], font=("Helvetica", 15))
            w.place(rely= 0.95 * i / float(len(GROEPERINGEN)) + 0.05, relx=0.3, anchor=CENTER)
            self.names[i].set(g)

            w = Label(self, textvariable=self.scores[i], font=("Helvetica", 15))
            w.place(rely= 0.95 * i / float(len(GROEPERINGEN)) + 0.05, relx=0.6, anchor=CENTER)
            self.scores[i].set("0")

        self.pack(fill=BOTH, expand=1)


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


    def chi_square_dist(self, orders_Chaos, orders_other):
        dist = 0
        for name, val in orders_Chaos:
            if val > 0:
                dist += ((val - orders_other[name])**2/val)

        return dist


    def update_scores(self):
        print("Update")

        # Get orders of Chaos
        orders_Chaos = self.get_total_orders_of_group('Chaos')




        scores = {}

        for i, (g, s) in enumerate(sorted(scores.items(), key=lambda x: x[1], reverse=True)):
            print(i, g, s)
            self.names[i].set(g)
            self.scores[i].set("%d" % s)

        print

        self.after(3000, self.update_scores)
        

def main():
  
    root = Tk()
    root.geometry("800x500")
    print('Running')
    app = Example(root)
    root.mainloop()  


    #     time.sleep(1)



if __name__ == '__main__':
    main()  
