#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from barkas import Barkas
from tkinter import Tk, Frame, BOTH, Label, StringVar, CENTER

DATUM = "2015-11-06"
DRANK = "Bier zwembadfeest"
GROEPERINGEN = ['Nobel', 'Krat', 'Bestuur 122', 'Chaos', 'Spetter', 'Quast', 'Octopus', 'McClan', 'Kurk', 'Apollo', 'Schranz', 'Asene', 'Kielzog', 'Scorpios', 'Fabula', 'TDC 66']
CONSUMPTIES = {'Fris': 2, 'Pul Fris': 6, 'Safari': 3, 'Apfelkorn': 3, 'Eristoff': 3, 'Jagermeister': 3, 'Likeur 43': 3, 'Pitcher bier': 6, 'Peach Tree ': 3}
S50 = {'bacardi razz': 40, 'honingwijn': 15}

class Example(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")   
         
        self.parent = parent
        

        self.names = {}
        self.scores = {}
        for i, g in enumerate(GROEPERINGEN):
            self.names[i] = StringVar()
            self.scores[i] = StringVar()

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

    def update_scores(self):
        print("Update")
        self.barkas = Barkas()

        # date = datetime.date(2015,11,26)
        date = datetime.date.today()

        scores = {}
        for g in GROEPERINGEN:
            score = 2 * self.barkas.get_number_of_beers(date, g)

            for (name, mult) in CONSUMPTIES.items():
                score += mult * self.barkas.get_number_of_consumptions(date, g, name)

            for (name, mult) in S50.items():
                score += mult * self.barkas.get_number_of_s50(date, g, name)

            scores[g] = score

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
