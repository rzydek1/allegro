import requests
import time
import message


class Auth:

    def __init__(self, client_id, client_basic64):

        self.oauth_url = "https://allegro.pl/auth/oauth/device"
        self.token_url = "https://allegro.pl/auth/oauth/token?grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Adevice_code"
        self.refresh_token_url = "https://allegro.pl/auth/oauth/token"

        self.client_id = client_id
        self.client_basic64 = client_basic64

        self.access_token = ''
        self.token_end_time = 0
        self.refresh_token = ''
        self.interval = 60

        self.headers = {'Content-type': 'application/x-www-form-urlencoded',
                        'Authorization': 'Basic {}'.format(self.client_basic64)}

    def get_access_code(self):

        access_code_response = False

        try:
            access_code_response = requests.post(self.oauth_url,
                                                 params={'client_id': self.client_id},
                                                 headers=self.headers)
        except requests.exceptions.RequestException as e:
            print(e)
            return -1

        if access_code_response:
            self.interval = int(access_code_response.json()['interval'])
            device_code = access_code_response.json()['device_code']
            verification_uri = access_code_response.json()['verification_uri_complete']

            print("Udało się uzyskać access_code!\nverification_uri: {}".format(verification_uri))

            return device_code

    def get_token(self):

        device_code = self.get_access_code()

        while True:

            token_response = False

            try:
                token_response = requests.post(self.token_url,
                                               data={'device_code': device_code},
                                               headers=self.headers)
            except requests.exceptions.Timeout:
                print('Przekroczono czas oczekiwania na access_token,\nPonowna próba pobrania...')
                continue
            except requests.exceptions.RequestException as e:
                print(e)
                return False

            if token_response:
                print('uzyskano token!')

                self.refresh_token = token_response.json()['refresh_token']
                self.access_token = token_response.json()['access_token']
                self.token_end_time = time.time() + token_response.json()['expires_in']

                msg = '''
                Token wygenerowany.

                data wygaśnięcia tokenu: {}
                '''.format(time.ctime(self.token_end_time))

                # message.send_email('Wygenerowano token', msg)
                break

            time.sleep(self.interval)

    def update_token(self):

        print('odswiezanie tokena')

        while True:
            try:
                refresh_response = requests.post(self.refresh_token_url,
                                                 data={'refresh_token': self.refresh_token,
                                                       'grant_type': 'refresh_token'},
                                                 headers=self.headers)
            except requests.exceptions.Timeout:
                print('Przekroczono czas oczekiwania na refresh_token,\nPróba ponownego pobrania...')
                time.sleep(60)
                continue
            except requests.exceptions.RequestException as e:
                print(e)
                return False

            if refresh_response:
                msg = '''
                Token odświeżony.
                
                Czas przed upłynięciem ważności poprzedniego tokenu: {} godzin
                '''.format((self.token_end_time - time.time()) / 60 / 60)

                self.refresh_token = refresh_response.json()['refresh_token']
                self.access_token = refresh_response.json()['access_token']
                self.token_end_time = time.time() + refresh_response.json()['expires_in']

                # message.send_email('odswiezanie tokenu',msg)
                break

            time.sleep(self.interval)

    def check_token(self):

        if self.token_end_time - time.time() < 2 * 60 * 60:
            return False

        return True

    def authorize(self):

        if self.access_token != '':
            if self.check_token():
                return self.access_token
            else:
                self.update_token()
        else:
            self.get_token()

        return self.access_token
