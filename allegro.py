import time

import authorization
from data_access import Data
import internet_check
import files


def allegro_service():
    """"function which runs the allegro module"""

    # read from config.txt values for authorization with allegro
    config = 'config.txt'

    client_id = files.find_value('client_id', config)
    client_basic64 = files.find_value('client_basic64', config)
    oauth_url = files.find_value('oauth_url', config)
    token_url = files.find_value('token_url', config)
    refresh_token_url = files.find_value('refresh_token_url', config)

    last_event = files.find_value('last_event', 'tmp.txt')

    auth = authorization.Auth(client_id, client_basic64, oauth_url, token_url, refresh_token_url)

    while True:

        # sprawdz czy jest internet
        if internet_check.check():

            try:
                access_token = auth.authorize()
            except authorization.AuthException as e:
                print(e)
                break

            # jezeli autoryzacja sie powiodla
            if access_token:
                data = Data(access_token)

                if not data.check_last_event(last_event):
                    if last_event == '':
                        last_event = data.get_latest_event()

                    save_attempts = 0
                    while save_attempts < 5:

                        save_flag = data.save_orders(last_event)
                        # pobierz najnowsze zamowienia i zapisz do bazy danych
                        if save_flag != -1:
                            last_event = data.get_latest_event()
                            files.save_value('last_event', last_event, 'tmp.txt')
                            break

                        save_attempts += 1

                    else:
                        # TODO: obsłużyć ten wyjątek
                        print('Houston mamy problem')

        time.sleep(5 * 60)

