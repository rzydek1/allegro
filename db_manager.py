import sqlite3
import uuid

class DBManager:

    def __enter__(self):
        try:
            self.conn = sqlite3.connect('allegro.db')
            self.c = self.conn.cursor()
            self.db_opened = True
            self.create_tables()
        except Exception as e:
            print(e)
            self.db_opened = False
            
        return self

    def create_tables(self):

        if self.db_opened:
            self.c.execute('''CREATE TABLE IF NOT EXISTS orders
                (OrderID text PRIMARY KEY,
                BuyerID text,
                AddressID text,
                OrderStatus text,
                PaymentType text,
                DeliveryMethod text,
                TotalToPay REAL,
                MessageToSeller text,
                TransactionTime text, 
                    FOREIGN KEY (AddressID) REFERENCES deliveryAddresses(AddressID))''')

            self.c.execute('''CREATE TABLE IF NOT EXISTS deliveryAddresses
                (AddressID text PRIMARY KEY,
                FirstName text,
                LastName text,
                Street text,
                City text,
                ZipCode text,
                PhoneNumber text)''')

            self.c.execute('''CREATE TABLE IF NOT EXISTS buyers
                (BuyerID text PRIMARY KEY,
                Email text,
                Login text,
                PhoneNumber text)''')

            self.c.execute('''CREATE TABLE IF NOT EXISTS buyerAddress
                (BuyerID text,
                AddressID text,
                    PRIMARY KEY (BuyerID, AddressID),
                    FOREIGN KEY (BuyerID) REFERENCES buyers(BuyerID),
                    FOREIGN KEY (AddressID) REFERENCES deliveryAddresses(AddressID))''')

    def print_values(self):

        if self.db_opened:

            for row in self.c.execute('SELECT * FROM orders'):
                print('order: {}'.format(row))

            for row in self.c.execute('\nSELECT * FROM deliveryAddresses'):
                print('deliveryAddress: {}'.format(row))

            for row in self.c.execute('\nSELECT * FROM buyers'):
                print('Buyer: {}'.format(row))

            for row in self.c.execute('\nSELECT * FROM buyerAddress'):
                print('BuyerAddress: {}'.format(row))

    def add_buyer(self, buyer):

        buyer = (buyer['id'],
                   buyer['email'],
                   buyer['login'],
                   buyer['phoneNumber'])

        try:
            if self.db_opened:
                self.c.execute('INSERT INTO buyers VALUES (?, ?, ?, ?)', buyer)
        except sqlite3.IntegrityError as e:
            print(e)
            return False
        except Exception as e:
            print(e)
            return False
        
        return True

    def add_delivery_address(self, buyer_id, address_id, delivery):

        if not address_id[1]:
            return True

        address = (address_id[0], delivery['firstName'], delivery['lastName'], delivery['street'],
                    delivery['city'], delivery['zipCode'], delivery['phoneNumber'])

        try:
            if self.db_opened:
                self.c.execute('INSERT INTO deliveryAddresses VALUES (?, ?, ?, ?, ?, ?, ?)', address)
        except sqlite3.IntegrityError as e:
            print(e)
            return False
        except Exception as e:
            print(e)
            return False

        return True

    def add_order(self, order_id, buyer_id, address_id, order_status, payment_type,
                  delivery_method, total_to_pay, message_to_seller,
                  transaction_time):

        order = (order_id, buyer_id, address_id[0], order_status, payment_type, delivery_method,
                  total_to_pay, message_to_seller, transaction_time)

        try:
            if self.db_opened:
                self.c.execute('INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', order)
        except sqlite3.IntegrityError as e:
            print(e)
            return False
        except Exception as e:
            print(e)
            return False

        return True

    def connect_address_buyer(self, buyer_id, address_id):
        if self.db_opened:
            self.c.execute('SELECT 1 FROM buyerAddress WHERE BuyerID=? and AddressID=?',
                            (buyer_id, address_id[0],))

            if self.c.fetchone() is None:
                try:
                    self.c.execute('INSERT INTO buyerAddress VALUES (?, ?)',
                                        (buyer_id, address_id[0],))
                    return True
                except sqlite3.IntegrityError as e:
                    print(e)
                    return False
                except Exception as e:
                    print(e)
                    return False
                
            return True

    def find_order_by_id(self, order_id):
        if self.db_opened:
            self.c.execute('SELECT 1 FROM orders WHERE OrderID=?', (order_id,))

            if self.c.fetchone() is None:
                return False

        return True

    def find_delivery_address_id(self, delivery):
        
        self.c.execute('''SELECT AddressID FROM deliveryAddresses WHERE
                    FirstName=? and
                    LastName=? and
                    Street=? and
                    City=? and
                    ZipCode=? and
                    PhoneNumber=?''', (delivery['firstName'], delivery['lastName'], 
                        delivery['street'], delivery['city'], delivery['zipCode'], delivery['phoneNumber'],))

        data = self.c.fetchone()

        if data is None:
            return (str(uuid.uuid1()), False,)

        return (data[0], True,)

    def __exit__(self, exc_type, exc_val, exc_tb):

        if self.db_opened:
            self.conn.commit()
            self.conn.close()
