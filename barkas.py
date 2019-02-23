import random
import datetime
import pymysql.cursors
import time
from fuzzywuzzy import process

class Barkas(object):
    def __init__(self):
        self.connection = pymysql.connect(host='192.168.1.1',
                                          user='barkasread',
                                          password='lezen',
                                          db='barkas_1_0_prod',
                                          charset='utf8mb4',
                                          autocommit=True,
                                          cursorclass=pymysql.cursors.DictCursor)

        self.prijslijst_version = self.get_prijslijst_version()
        self.product_ids = {}
        self.product_names = {}
        self.bon_debtor = {}
        self.debtor_ids = {}
        self.debtor_names = {}
        self.day_to_bon_ids_next_update = datetime.datetime.now()
        self.day_to_bon_ids = {}

    def get_prijslijst_version(self):
        with self.connection.cursor() as cursor:
            sql = "SELECT Prijs_Versie FROM prijs ORDER BY Prijs_ID DESC LIMIT 1"
            cursor.execute(sql)
            result = cursor.fetchone()
            return result['Prijs_Versie']

    def find_product_id(self, product):
        if product not in self.product_ids:
            with self.connection.cursor() as cursor:
                sql = "SELECT * FROM prijs WHERE Prijs_Versie = %s"
                cursor.execute(sql, (self.prijslijst_version, ) )
                result = cursor.fetchall()
                
                if result:
                    product_name_id = {r['Prijs_Naam']: r['Prijs_ID'] for r in result}
                    choices = set(product_name_id.keys())

                    choices = set([r['Prijs_Naam'] for r in result])
                else:
                    raise RuntimeError("Product Not Found")

            # Fuzzy match
            exact_product, certainty = process.extractOne(product, choices)
            if certainty == 100:
                product_id = product_name_id[exact_product]
                self.product_ids[product] = product_id
                print("Product id found with max certainty:", exact_product, product_id)
            elif certainty >= 80:
                product_id = product_name_id[exact_product]
                self.product_ids[product] = product_id  
                print("Product id found (" + str(certainty) + "%):", exact_product, product_id)
            else:
                raise RuntimeError("Product not found")                  
            

        return self.product_ids[product]

    def get_product_name(self, product_id):
        if product_id not in self.product_names:
            with self.connection.cursor() as cursor:
                sql = "SELECT Prijs_Naam FROM prijs WHERE Prijs_Versie = %s AND Prijs_ID = %s"
                corsor.execute(sql, (self.prijslijst_version, product_id, ) )
                result = cursor.fetchone()
                if result:
                    self.debtor_names[debtor_id] = result['Prijs_Naam'].strip()
        return self.product_names[product_id]

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

    def get_debtor_name(self, debtor_id):
        if debtor_id not in self.debtor_names:
            with self.connection.cursor() as cursor:
                sql = "SELECT Debiteur_Naam FROM debiteur WHERE Debiteur_Actief = 1 AND Debiteur_ID = %s"
                corsor.execute(sql, (debtor_id, ))
                result = cursor.fetchone()
                if result:
                    self.debtor_names[debtor_id] = result['Debiteur_Naam'].strip()
        return self.debtor_names[debtor_id]

    def get_bon_debtor(self, bon_id):
        if bon_id not in self.bon_debtors:
            with self.connection.cursor() as cursor:
                sql = "SELECT Bon_Debiteur From bon WHERE Bon_ID = %s"
                cursor.execute(sql, (bon_id, ))
                result = cursor.fetchone()
                if result:
                    self.bon_debtor[bon_id] = int(result['Bon_Debiteur'])
        return self.bon_debtor[bon_id]

    def get_number_of_consumptions(self, date, debtor, consumption_name):
        """Returns the number of consumption for a debtor on a specific date"""

        product_id = self.find_product_id(consumption_name)
        debtor_id = self.find_debtor_id(debtor)
        with self.connection.cursor() as cursor:
            sql = "SELECT SUM(Bestelling_AantalS) AS aantalS FROM `bestelling` WHERE Bestelling_Bon IN (SELECT Bon_ID from bon WHERE Bon_Debiteur = %s AND Bon_Datum = %s) AND Bestelling_Wat = %s"
            cursor.execute(sql, (debtor_id, date.isoformat(), product_id, ))
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
            sql = "SELECT SUM(Bestelling_AantalS50) AS aantalS50 FROM `bestelling` WHERE Bestelling_Bon IN (SELECT Bon_ID from bon WHERE Bon_Debiteur = %s AND Bon_Datum = %s) AND Bestelling_Wat = %s"
            cursor.execute(sql, (debtor_id, date.isoformat(), product_id, ))
            result = cursor.fetchone()

            aantal = result['aantalS50']
            if aantal is None:
                return 0
            return aantal

    def get_number_of_beers(self, date, debtor):
        number_of_beers_consumption = [('Bier', 1)]
        result = 0
        for consumption, amount in number_of_beers_consumption:
            result += amount * self.get_number_of_consumptions(date, debtor, consumption)

        return result

    def get_todays_orders_since(self, ts_from):
        return self.get_orders_of_day_since( (datetime.datetime.now() - datetime.timedelta(hours = 12)).date(), ts_from )
    def get_orders_of_day_since(self, date_bon, ts_from, limit=None):
        bon_ids = self.get_bon_ids_of_day(date_bon)
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM bestelling WHERE Bestelling_Bon IN %s AND Bestelling_Time > %s ORDER BY Bestelling_Time ASC"
            args = ( tuple(bon_ids), ts_from, )
            if limit is not None:
                sql += " LIMIT %s"
                args += ( limit, )
            cursor.execute(sql, args)
            bestellingen = cursor.fetchall()
        return bestellingen

    def get_orders_of_day_stream(self, date_bon):
        batch_size = 10
        str_lead = 'Bestelling_Aantal'

        last_time = 0
        while True:
            batch = self.get_orders_of_day(date_bon, last_time, limit=batch_size)
            if not batch:
                time.sleep(1)
                continue
            for order in batch:
                last_time = int(order['Bestelling_Time'])
                debtor_id = self.get_bon_debtor(order['Bestelling_Bon'])
                product_id = order['Bestelling_Wat']
                debtor_name = self.get_debtor_name(debtor_id)
                product_name = self.get_product_name(product_id)
                used_aantal = [(k[len(str_lead):], v) for k,v in order.items() if k.startswith(str_lead) and v > 0]
                active_type, amount = used_aantal[0]
                yield {
                    'timestamp' : last_time,
                    'group'     : debtor_name,
                    'product'   : product_name,
                    'type'      : active_type,
                    'amount'    : amount,
                }

    # New bonnen will be opened during the day, but cache for short periods
    def get_bon_ids_of_day(self, date_bon):
        if self.date_to_bon_ids_next_update <= datetime.datetime.now():
            self.date_to_bon_ids = {}
        if date_bon not in self.date_to_bon_ids:
            with self.connection.cursor() as cursor:
                sql = "SELECT Bon_Id FROM bon WHERE Bon_Datum = %s"
                cursor.execute(sql, ( date_bon.isoformat(), ))
                bon_ids = [int(row['Bon_Id']) for row in cursor.fetchall()]
                self.date_to_bon_ids[date_bon] = bon_ids
                self.date_to_bon_ids_next_update = datetime.datetime.now() + datetime.timedelta(minutes=1)
        return self.date_to_bon_ids[date_bon]

if __name__ == '__main__':
    b = Barkas()
    print(b.get_number_of_consumptions(datetime.date.today(), 'Bestuur 119', 'Pul Bier'))
    print(b.get_number_of_s50(datetime.date.today(), 'Chaos', 'Apfelkorn'))
    print(b.get_number_of_consumptions(datetime.date(2015, 11, 26), 'Bestuur 119', 'Pul Bier'))
    print(b.get_number_of_beers(datetime.date(2015, 11, 26), 'Bestuur 119'))
    print(b.get_number_of_beers(datetime.date.today(), 'Chaos'))
