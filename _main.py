import time
import datetime

import authorization
from data_access import Data
import internet_check

client_id = "9d07cbc64b89450e8665e4149e1dc617"
client_basic64 = 'OWQwN2NiYzY0Yjg5NDUwZTg2NjVlNDE0OWUxZGM2MTc6VHZjdXlZa0JvZkVpSUc5bXpxSm9LeFE0M3ZRWWh5dzNmZ2U1RE5OZERiMGNZMGpkNnBLRE9VdHJrU3YyVEx6ZA=='

auth = authorization.Auth(client_id, client_basic64)
last_event = ''

while True:

    # sprawdz czy jest internet
    if internet_check.check():

        access_token = auth.authorize()

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
                    if save_flag == 1:
                        last_event = data.get_latest_event()
                        break

                    elif save_flag == 0:
                        break

                    save_attempts += 1
                
                else:
                    # TODO: obsłużyć ten wyjątek
                    print('Houston mamy problem')

    time.sleep(5 * 60)
