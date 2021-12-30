import requests
import os
from dotenv import load_dotenv

load_dotenv()

status = 0
params = {'status': status}
r = requests.post('https://bitwardentest.hund.io/state_webhook/watchdog/61cd8a01386fb37c3d04b049', headers = {"X-WEBHOOK-KEY": os.environ.get('X-WEBHOOK-KEY')}, params=params)

r.raise_for_status()