import requests
import os
from dotenv import load_dotenv
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

load_dotenv()

options = Options()
if os.environ.get("CI") != None:
    options.headless = True

browser = Firefox(
    service=Service("./geckodriver"), options=options
)

try:
    browser.get("https://vault.bitwarden.com/#/")
    assert browser.title == "Bitwarden Web Vault"

    #username = browser.find_element_by_id("email")
    #password = browser.find_element_by_id("masterPassword")

    #username.send_keys(os.environ.get("email"))
    #password.send_keys(os.environ.get("masterpassword"))

    #browser.find_elements_by_class_name("btn btn-primary btn-block btn-submit").click()
finally:
    browser.quit()

status = 0
params = {"status": status}
r = requests.post(
    "https://bitwardentest.hund.io/state_webhook/watchdog/61cd8a01386fb37c3d04b049",
    headers={"X-WEBHOOK-KEY": os.environ.get("X_WEBHOOK_KEY")},
    params=params,
)

r.raise_for_status()
