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

    def check_base(self):

        if self.db_opened:
            return True

        return False

    def create_tables(self):

        self.c.execute('''CREATE TABLE IF NOT EXISTS orders
            (OrderID text PRIMARY KEY,
            BuyerID text,
            AddressID text,
            OrderStatus text,
            PaymentType text,
            DeliveryMethod text,
            TotalToPay REAL,
            MessageToSeller text,
            OccurredAt text, 
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
            PhoneNumber text,
            FirstOccurrence text)''')

        self.c.execute('''CREATE TABLE IF NOT EXISTS buyerAddress
            (BuyerID text,
            AddressID text,
                PRIMARY KEY (BuyerID, AddressID),
                FOREIGN KEY (BuyerID) REFERENCES buyers(BuyerID),
                FOREIGN KEY (AddressID) REFERENCES deliveryAddresses(AddressID))''')

        self.c.execute('''CREATE TABLE IF NOT EXISTS orderItems
            (OrderID text,
            ItemID text,
            quantity INTEGER,
            PRIMARY KEY (OrderID, ItemID),
            FOREIGN KEY (OrderID) REFERENCES orders(OrderID),
            FOREIGN KEY (ItemID) REFERENCES items(ItemID))''')

        self.c.execute('''CREATE TABLE IF NOT EXISTS items
            (ItemID text PRIMARY KEY,
            ItemName text,
            Price REAL)''')

    def print_values(self):

        for row in self.c.execute('SELECT * FROM orders'):
            print('order: {}'.format(row))

        for row in self.c.execute('SELECT * FROM deliveryAddresses'):
            print('deliveryAddress: {}'.format(row))

        for row in self.c.execute('SELECT * FROM buyers'):
            print('Buyer: {}'.format(row))

        for row in self.c.execute('SELECT * FROM buyerAddress'):
            print('BuyerAddress: {}'.format(row))

        for row in self.c.execute('SELECT * FROM items'):
            print('Item: {}'.format(row))

        for row in self.c.execute('SELECT * FROM orderItems'):
            print('OrderItems: {}'.format(row))

        self.c.execute('SELECT * FROM items')

        data = self.c.fetchall()
        print(len(data))

    def add_buyer(self, buyer, time_stamp):

        buyer = (buyer['id'],
                 buyer['email'],
                 buyer['login'],
                 buyer['phoneNumber'],
                 time_stamp)

        try:
            self.c.execute('INSERT INTO buyers VALUES (?, ?, ?, ?, ?)', buyer)
        except sqlite3.IntegrityError as e:
            return 0
        except Exception as e:
            print(e)
            return -1

        return 1

    def add_delivery_address(self, address_id, delivery):

        if address_id[1]:
            return True

        address = (address_id[0], delivery['firstName'], delivery['lastName'], delivery['street'],
                   delivery['city'], delivery['zipCode'], delivery['phoneNumber'])

        try:
            self.c.execute('INSERT INTO deliveryAddresses VALUES (?, ?, ?, ?, ?, ?, ?)', address)
        except sqlite3.IntegrityError as e:
            return 0
        except Exception as e:
            print(e)
            return -1

        return 1

    def add_order(self, order_id, buyer_id, address_id, order_status, payment_type,
                  delivery_method, total_to_pay, message_to_seller,
                  transaction_time):

        order = (order_id, buyer_id, address_id[0], order_status, payment_type, delivery_method,
                 total_to_pay, message_to_seller, transaction_time)

        try:
            self.c.execute('INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', order)
        except sqlite3.IntegrityError as e:
            return 0
        except Exception as e:
            print(e)
            return -1

        return 1

    def add_item(self, item_id, item_name, item_price):

        if self.find_item_by_id(item_id):
            return True

        try:
            self.c.execute('INSERT INTO items VALUES(?, ?, ?)', (item_id, item_name, item_price,))
        except sqlite3.IntegrityError as e:
            return 0
        except Exception as e:
            print(e)
            return -1

        return 1

    def connect_order_item(self, order_id, item_id, quantity):

        try:
            self.c.execute('INSERT INTO orderItems VALUES (?, ?, ?)', (order_id, item_id, quantity,))
        except sqlite3.IntegrityError:
            print('This connection actually exists')
            return 0
        except Exception as e:
            print(e)
            return -1

        return 1

    def connect_address_buyer(self, buyer_id, address_id):

        if self.c.fetchone() is None:
            try:
                self.c.execute('INSERT INTO buyerAddress VALUES (?, ?)',
                               (buyer_id, address_id[0],))
            except sqlite3.IntegrityError:
                print('This connection actually exists')
                return 0
            except Exception as e:
                print(e)
                return -1

        return 1

    def find_order_by_id(self, order_id):
        """Check if there is order with given id"""

        if self.get_order_by_id(order_id):
            return True

        return False

    def find_delivery_address_id(self, delivery):
        """Look for given delivery address in DB. Generate a new address_id if the address does not exists,
        otherwise return the existing address_id"""

        self.c.execute('''SELECT AddressID FROM deliveryAddresses WHERE
                    FirstName=? and
                    LastName=? and
                    Street=? and
                    City=? and
                    ZipCode=? and
                    PhoneNumber=?''', (delivery['firstName'], delivery['lastName'],
                                       delivery['street'], delivery['city'], delivery['zipCode'],
                                       delivery['phoneNumber'],))

        data = self.c.fetchone()

        if data is None:
            return str(uuid.uuid1()), False,

        return data[0], True,

    def find_item_by_id(self, item_id):

        if self.get_item_by_id(item_id):
            return True

        return False

    def get_order_by_id(self, order_id):

        self.c.execute('SELECT * FROM orders WHERE OrderID=?', (order_id,))

        data = self.c.fetchone()

        if data is None:
            return False

        return data

    def get_delivery_address_by_id(self, address_id):

        self.c.execute('SELECT * FROM deliveryAddresses WHERE AddressID=?', (address_id,))

        data = self.c.fetchone()
        return data[0]

    def get_buyer_by_id(self, buyer_id):

        self.c.execute('SELECT * FROM buyers WHERE BuyerID=?', (buyer_id,))

        data = self.c.fetchone()
        return data

    def get_last_buyers(self, limit):

        self.c.execute('SELECT * FROM buyers ORDER BY date(firstOccurrence) LIMIT ?', (limit,))

        data = self.c.fetchall()

        return data

    def get_buyer_delivery_addresses(self, buyer_id):

        self.c.execute('SELECT AddressID FROM buyerAddress WHERE BuyerID=?', (buyer_id,))

        data = []

        for address in self.c.fetchall():
            data.append(self.get_delivery_address_by_id(address))

        if len(data) == 0:
            return False

        return data

    def get_last_orders(self, limit):

        self.c.execute('SELECT * FROM orders ORDER BY date(OccurredAt) LIMIT ?', (limit,))

        data = self.c.fetchall()

        return data

    def get_orders_from(self, from_date, limit):

        self.c.execute('SELECT * FROM orders WHERE OccurredAt > ? ORDER BY date(OccurredAt) LIMIT ?',
                       (from_date, limit,))

        data = self.c.fetchall()

        return data

    def get_orders_from_to(self, after_date, before_date):

        self.c.execute('SELECT * FROM orders WHERE OccurredAt > ? and OccurredAt < ? ORDER BY date(OccurredAt)',
                       (after_date, before_date,))

        data = self.c.fetchall()

        return data

    def get_item_by_id(self, item_id):

        self.c.execute('SELECT * FROM items WHERE ItemID=?', (item_id,))

        data = self.c.fetchone()

        if data is None:
            return False

        return data[0]

    def get_order_items(self, order_id):

        self.c.execute('SELECT ItemID FROM orderItems WHERE OrderID=?', (order_id,))

        data = []

        for item in self.c.fetchall():
            data.append(self.c.execute('SELECT * FROM items WHERE ItemID=?', (item,)))

        if len(data) == 0:
            return False

        return data

    def __exit__(self, exc_type, exc_val, exc_tb):

        if self.db_opened:
            self.conn.commit()
            self.conn.close()


with DBManager() as db:
    datar = db.get_last_buyers(5)
    for row in datar:
        print(row)
