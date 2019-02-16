import datetime
from barkas import Barkas

class Bestelling():

    groepering = ''
    bestellingen = {'Fris': 0, 'Pul Fris': 0, 'Safari': 0, 'Apfelkorn': 0, 'Eristoff': 0, 'Jagermeister': 0, 'Likeur 43': 0, 'Pitcher bier': 0, 'Peach Tree ': 0, 'Bier': 0, 'bacardi razz': 0, 'honingwijn': 0}

    def __init__(self, _groep):
        groepering = _groep

    # Upon a collection of items being passed into this function, return the difference between bestellingen and the collection.
    # Also, set bestellingen to this dictionary.
    def get_diff_between_bestellingen_and_dict(self, other):
        res = {}
        for name, val in other:
            res[name] = val - self.bestellingen[name]

        return res