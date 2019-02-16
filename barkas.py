import random
import datetime
import pymysql.cursors
from fuzzywuzzy import process

class Barkas(object):
    def __init__(self):
        self.connection = pymysql.connect(host='192.168.1.1',
                                          user='barkasread',
                                          password='lezen',
                                          db='barkas_1_0_prod',
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)

        self.prijslijst_version = self.get_prijslijst_version()
        self.product_ids = {}
        self.debtor_ids = {}

    def get_prijslijst_version(self):
        with self.connection.cursor() as cursor:
            sql = "SELECT Prijs_Versie FROM prijs ORDER BY Prijs_ID DESC LIMIT 1"
            cursor.execute(sql)
            result = cursor.fetchone()
            return result['Prijs_Versie']

    def find_product_id(self, product):
        if product not in self.product_ids:
            with self.connection.cursor() as cursor:
                sql = "SELECT * FROM prijs WHERE Prijs_Versie = " + str(self.prijslijst_version)
                cursor.execute(sql)
                result = cursor.fetchall()
                
                if result:
                    product_name_id = {r['Prijs_Naam']: r['Prijs_ID'] for r in result}
                    choices = set(product_name_id.keys())

                    choices = set([r['Prijs_Naam'] for r in result])
                else:
                    raise RuntimeError("Product Not Found")

            # Fuzzy match
            exact_product, certainty = process.extractOne(product, choices)
            if certainty >= 80:
                product_id = product_name_id[exact_product]
                self.product_ids[product] = product_id  
                print("Product id found (" + str(certainty) + "%):", exact_product, product_id)
            else:
                raise RuntimeError("Product not found")                  
            

        return self.product_ids[product]

    def find_debtor_id(self, debtor):
        if debtor not in self.debtor_ids:
            with self.connection.cursor() as cursor:
                sql = "SELECT * FROM debiteur WHERE Debiteur_Actief = 1"
                cursor.execute(sql)
                result = cursor.fetchall()
                
                if result:
                    debtor_name_id = {r['Debiteur_Naam']: r['Debiteur_ID'] for r in result}
                    choices = set(debtor_name_id.keys())

            exact_name, certainty = process.extractOne(debtor, choices)
            debtor_id = debtor_name_id[exact_name]

            if certainty > 60:
                print("Debtor found (%d%%): %s - %s" % (certainty, exact_name, debtor_id))
                self.debtor_ids[debtor] = debtor_id
            else:
                raise RuntimeError("Debtor not found")

        return self.debtor_ids[debtor]

    def get_number_of_consumptions(self, date, debtor, consumption_name):
        """Returns the number of consumption for a debtor on a specific date"""

        product_id = self.find_product_id(consumption_name)
        debtor_id = self.find_debtor_id(debtor)
        with self.connection.cursor() as cursor:
            sql = "SELECT SUM(Bestelling_AantalS) AS aantalS FROM `bestelling` WHERE Bestelling_Bon IN (SELECT Bon_ID from bon WHERE Bon_Debiteur = %d AND Bon_Datum = '%s') AND Bestelling_Wat = %d" % (debtor_id, date.isoformat(), product_id)
            cursor.execute(sql)
            result = cursor.fetchone()

            aantal = result['aantalS']
            if aantal is None:
                return 0
            return aantal

    def get_number_of_s50(self, date, debtor, consumption_name):
        """Returns the number of consumption for a debtor on a specific date"""

        product_id = self.find_product_id(consumption_name)
        debtor_id = self.find_debtor_id(debtor)
        with self.connection.cursor() as cursor:
            sql = "SELECT SUM(Bestelling_AantalS50) AS aantalS50 FROM `bestelling` WHERE Bestelling_Bon IN (SELECT Bon_ID from bon WHERE Bon_Debiteur = %d AND Bon_Datum = '%s') AND Bestelling_Wat = %d" % (debtor_id, date.isoformat(), product_id)
            cursor.execute(sql)
            result = cursor.fetchone()

            aantal = result['aantalS50']
            if aantal is None:
                return 0
            return aantal

    def get_number_of_beers(self, date, debtor):
        number_of_beers_consumption = [('Pul Bier', 3), ('Pul Bier Korting', 3), ('Meter', 12), ('Bier', 1), ('Pitcher Bier', 2)]
        result = 0
        for consumption, amount in number_of_beers_consumption:
            result += amount * self.get_number_of_consumptions(date, debtor, consumption)

        return result



if __name__ == '__main__':
    b = Barkas()
    print(b.get_number_of_consumptions(datetime.date.today(), 'Bestuur 119', 'Pul Bier'))
    print(b.get_number_of_s50(datetime.date.today(), 'Chaos', 'Apfelkorn'))
    print(b.get_number_of_consumptions(datetime.date(2015, 11, 26), 'Bestuur 119', 'Pul Bier'))
    print(b.get_number_of_beers(datetime.date(2015, 11, 26), 'Bestuur 119'))