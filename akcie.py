#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import pymysql.cursors
import time
import datetime
from barkas import Barkas
from tkinter import Tk, Frame, BOTH, Label, StringVar, CENTER

DATUM = "2015-11-06"
DRANK = "Bier zwembadfeest"
GROEPERINGEN = ['Nobel', 'Krat', 'Bestuur 122', 'Chaos', 'Spetter', 'Quast', 'Octopus', 'McClan', 'Kurk', 'Apollo', 'Schranz', 'Asene', 'Kielzog', 'Scorpios', 'Fabula', 'TDC 66']

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
        self.update_scores()
    
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
            score += 2 * self.barkas.get_number_of_consumptions(date, g, 'Fris')
            score += 6 * self.barkas.get_number_of_consumptions(date, g, 'Pul Fris')
            score += 3 * self.barkas.get_number_of_consumptions(date, g, 'Safari')
            score += 3 * self.barkas.get_number_of_consumptions(date, g, 'Apfelkorn')
            score += 3 * self.barkas.get_number_of_consumptions(date, g, 'Eristoff')
            score += 3 * self.barkas.get_number_of_consumptions(date, g, 'Jagermeister')
            score += 3 * self.barkas.get_number_of_consumptions(date, g, 'Likeur 43')
            score += 6 * self.barkas.get_number_of_consumptions(date, g, 'Pitcher bier')
            score += 40 * self.barkas.get_number_of_s50(date, g, 'bacardi razz')
            score += 15 * self.barkas.get_number_of_s50(date, g, 'honingwijn')
            score += 3 * self.barkas.get_number_of_consumptions(date, g, 'Peach Tree ')
            score += 2 * self.barkas.get_number_of_beers(datetime.date(2015,11,30), g)
            score += 2 * self.barkas.get_number_of_consumptions(datetime.date(2015,11,30), g, 'Fris')
            score += 6 * self.barkas.get_number_of_consumptions(datetime.date(2015,11,30), g, 'Pul Fris')
            score += 3 * self.barkas.get_number_of_consumptions(datetime.date(2015,11,30), g, 'Safari')
            score += 3 * self.barkas.get_number_of_consumptions(datetime.date(2015,11,30), g, 'Apfelkorn')
            score += 3 * self.barkas.get_number_of_consumptions(datetime.date(2015,11,30), g, 'Eristoff')
            score += 3 * self.barkas.get_number_of_consumptions(datetime.date(2015,11,30), g, 'Jagermeister')
            score += 3 * self.barkas.get_number_of_consumptions(datetime.date(2015,11,30), g, 'Likeur 43')
            score += 6 * self.barkas.get_number_of_consumptions(datetime.date(2015,11,30), g, 'Pitcher bier')
            score += 40 * self.barkas.get_number_of_s50(datetime.date(2015,11,30), g, 'bacardi razz')
            score += 15 * self.barkas.get_number_of_s50(datetime.date(2015,11,30), g, 'honingwijn')
            score += 3 * self.barkas.get_number_of_consumptions(datetime.date(2015,11,30), g, 'Peach Tree ')

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
    app = Example(root)
    root.mainloop()  


    #     time.sleep(1)



if __name__ == '__main__':
    main()  
