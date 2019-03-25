import requests

import db_manager


class Data:

    def __init__(self, access_token, data_url='https://api.allegro.pl'):
        self.access_token = access_token
        self.data_url = data_url

        self.headers = {}
        self.headers['charset'] = 'utf-8'
        self.headers['Accept-Language'] = 'pl-PL'
        self.headers['Content-Type'] = 'application/json'
        self.headers['Accept'] = 'application/vnd.allegro.beta.v1+json'
        self.headers['Authorization'] = "Bearer {}".format(self.access_token)

    def get_orders(self, last_actualization):

        with requests.Session() as session:
            session.headers.update(self.headers)

            response = session.get(self.data_url + '/order/checkout-forms',
                                   params={'lineItems.boughtAt.gte': last_actualization})

            if len(response.json()['checkoutForms']) == 0:
                print('brak zamowien')
                return -1
            else:
                print('Ilosc zamowien: {}'.format(len(response.json()['checkoutForms'])))

                return response.json()

    def save_orders(self, last_actualization):

        data = self.get_orders(last_actualization)
        db_success_flag = False

        if data != -1:
            with db_manager.DBManager() as db:
                for order in data['checkoutForms']:

                    if not db.find_order_by_id(order['id']):

                        address_id = db.find_delivery_address_id(order['delivery']['address'])

                        db_success_flag = db.add_buyer(order['buyer'])
                        db_success_flag = db.add_delivery_address(order['buyer']['id'], address_id, order['delivery']['address'])
                        db_success_flag = db.add_order(order['id'],
                                                        order['buyer']['id'],
                                                        address_id,
                                                        order['status'],
                                                        order['payment']['type'],
                                                        order['delivery']['method']['name'],
                                                        order['summary']['totalToPay']['amount'],
                                                        order['messageToSeller'] if 'messageToSeller' in order else '',
                                                        order['payment']['finishedAt'] if 'finishedAt' in order['payment'] else last_actualization)
                        db_success_flag = db.connect_address_buyer(order['buyer']['id'], address_id)


                        if not db_success_flag:
                            print('Nie udało sie zapisać danych w bazie danych!')
                            return -1
                        
                db.print_values()
                return 1
        
        return 0
        