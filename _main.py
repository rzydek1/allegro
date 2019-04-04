import threading

import allegro
import REST

thread = threading.Thread(target=allegro.allegro_service)
thread.start()

REST.run_app()
