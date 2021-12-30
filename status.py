import requests
import os
from dotenv import load_dotenv
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

load_dotenv()

status = -1

options = Options()
if os.environ.get("CI") != None:
    options.headless = True

browser = Firefox(service=Service("./geckodriver"), options=options)
browser.set_page_load_timeout(15)

try:
    try:
        browser.get("https://vault.bitwarden.com/#/")
        assert browser.title == "Bitwarden Web Vault"

        username = WebDriverWait(browser, 10).until(
            expected_conditions.presence_of_element_located((By.ID, "email"))
        )
        password = WebDriverWait(browser, 10).until(
            expected_conditions.presence_of_element_located((By.ID, "masterPassword"))
        )

        username.send_keys(os.environ.get("email"))
        password.send_keys(os.environ.get("masterpassword"))
        password.send_keys(Keys.RETURN)


        try:
            an_item = WebDriverWait(browser, 10).until(
                expected_conditions.presence_of_element_located((By.LINK_TEXT, "Test item"))
            )
            an_item.click()

            item_username = (
                WebDriverWait(browser, 10)
                .until(
                    expected_conditions.presence_of_element_located(
                        (By.ID, "loginUsername")
                    )
                )
                .get_attribute("value")
            )
            item_password = (
                WebDriverWait(browser, 10)
                .until(
                    expected_conditions.presence_of_element_located(
                        (By.ID, "loginPassword")
                    )
                )
                .get_attribute("value")
            )

            assert item_username == "username"
            assert item_password == "password"
            status = 1
        except Exception as error:
            print("An degradation occurred: {}".format(error))
            status = 0

    except Exception as error:
        print("An outage occurred: {}".format(error))
        status = -1
finally:
    browser.quit()

print("Reporting a status: {}".format(status))
r = requests.post(
    "https://bitwardentest.hund.io/state_webhook/watchdog/61cd8a01386fb37c3d04b049",
    headers={"X-WEBHOOK-KEY": os.environ.get("X_WEBHOOK_KEY")},
    params={"status": status},
)

r.raise_for_status()
