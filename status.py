import requests
import os
import sys
import logging

from dotenv import load_dotenv

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()


options = Options()
if os.environ.get("CI") != None:
    options.headless = True

browser = Firefox(service=Service("./geckodriver"), options=options)
browser.set_page_load_timeout(15)


def report():
    logger.info("Reporting a status: {}".format(status))
    requests.post(
        "https://bitwardentest.hund.io/state_webhook/watchdog/61cd8a01386fb37c3d04b049",
        headers={"X-WEBHOOK-KEY": os.environ.get("WEBHOOK_KEY")},
        params={"status": status},
    ).raise_for_status()


def get(selector, or_else):
    try:
        return WebDriverWait(browser, 10).until(
            expected_conditions.presence_of_element_located(selector)
        )
    except Exception as error:
        logger.info(or_else)
        logger.exception(error)
        sys.exit(or_else)


def assertEqual(value, expected, or_else):
    if value != expected:
        logger.info(or_else)
        sys.exit(or_else)


try:
    ###### Outage ######
    status = -1
    browser.get("https://vault.bitwarden.com/#/")
    assert browser.title == "Bitwarden Web Vault"

    username = get((By.ID, "email"), "Couldn't get login email input")
    password = get((By.ID, "masterPassword2"), "Couldn't get login password input")

    username.send_keys(os.environ.get("EMAIL"))
    password.send_keys(os.environ.get("MASTER_PASSWORD"))
    password.send_keys(Keys.RETURN)

    ###### Degradation ######
    status = 0
    an_item = get((By.LINK_TEXT, "Test item"), "Couldn't get the test item")
    an_item.click()

    item_username = get(
        (By.ID, "loginUsername"), "Couldn't get the entry username"
    ).get_attribute("value")
    item_password = get(
        (By.ID, "loginPassword"), "Couldn't get the entry password"
    ).get_attribute("value")

    assertEqual(item_username, "username", "Entry username did not match")
    assertEqual(item_password, "password", "Entry password did not match")

    ###### Ok ######
    status = 1

finally:
    browser.quit()
    report()

assert status == 1
