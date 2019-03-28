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

    def check_last_event(self, event_id):
        """if last_event is the same return True, that seems if there isn't new event return True, else return False"""

        if self.get_latest_event() == event_id:
            return True

        return False

    def get_latest_event(self):

        with requests.Session() as session:
            session.headers.update(self.headers)

            latest_event = session.get(self.data_url + '/order/event-stats')

            if latest_event:
                return latest_event.json()['latestEvent']['id']

    def get_events(self, event_id):

        with requests.Session() as session:
            session.headers.update(self.headers)

            events = session.get(self.data_url + '/order/events',
                                 params={'from': event_id})

            if events:
                return events.json()

    def get_order_details(self, order_id):

        with requests.Session() as session:
            session.headers.update(self.headers)

            response = session.get(self.data_url + '/order/checkout-forms/{}'.format(order_id))

            return response.json()

    def save_orders(self, last_event):

        print(last_event)
        data = self.get_events(last_event)
        print(len(data['events']))

        try:

            with db_manager.DBManager() as db:
                if db.check_base():
                    for event in data['events']:

                        print('id: {},\noccurredAt: {}'.format(event['id'], event['occurredAt']))

                        time_stamp = event['occurredAt']
                        order = self.get_order_details(event['order']['checkoutForm']['id'])

                        if not db.find_order_by_id(order['id']):

                            address_id = db.find_delivery_address_id(order['delivery']['address'])

                            db.add_buyer(order['buyer'])
                            db.add_delivery_address(address_id, order['delivery']['address'])
                            db.add_order(order['id'],
                                         order['buyer']['id'],
                                         address_id,
                                         order['status'],
                                         order['payment']['type'],
                                         order['delivery']['method']['name'],
                                         order['summary']['totalToPay']['amount'],
                                         order['messageToSeller'] if 'messageToSeller' in order else '',
                                         time_stamp)
                            db.connect_address_buyer(order['buyer']['id'], address_id)

                            print('len(lineItems): {}'.format(len(order['lineItems'])))
                            for item in order['lineItems']:
                                db.add_item(item['offer']['id'],
                                            item['offer']['name'],
                                            item['price']['amount'])
                                db.connect_order_item(order['id'], item['offer']['id'], item['quantity'])

                    db.print_values()
                    return 1

        except KeyError as e:
            print('KeyError: {}'.format(e))
            return 0

        return 0
