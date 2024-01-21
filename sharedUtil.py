from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import time
import random

import traceback

class JobInfo:
    def __init__(self, description: str, title: str, company: str, location: str):
        self.description = description
        self.title = title
        self.company = company
        self.location = location



def strong_click(y: WebElement, driver: webdriver) -> None:
    #print(y.location['y'])

    t = str(max(y.location['y'] - 500, 0))
    #print(t)
    # need to test thoroughly should fix alot of ghost actions
    #some point we need to make a more robust way to get element onto screen
    # sometimes we need a + offset
    driver.execute_script("window.scrollTo(0," + t + ")")
    #driver.execute_script("arguments[0].scrollIntoView();", y)
    time.sleep(.1)
    try:
        y.click()
        return
    except (ElementClickInterceptedException, ElementNotInteractableException) :
        #traceback.print_exc()
        pass

    try:
        ActionChains(driver).move_to_element(y).click().perform()

        return
    except (ElementClickInterceptedException, ElementNotInteractableException):
        pass
    print('strong click did not fire')


def google_account_login(password, email, driver):
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@type = 'email']"))).send_keys(email)
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//span[text() = 'Next']"))).click()
    time.sleep(.5)
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@type = 'password']"))).send_keys(password)
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//span[text() = 'Next']"))).click()
    time.sleep(1)


def indeed_login(driver, user_info):
    time.sleep(.1)
    driver.get(
        'https://accounts.google.com/v3/signin/identifier?continue=https%3A%2F%2Fmail.google.com%2Fmail%2F&ifkv=AVQVeyyCBJPrKGzv6Rv2eA3gdl9_kQ5VkNMnFzQIG987MhtmbQLSPcqNldHxvx6HIYZYpwbSYl2gXQ&rip=1&sacu=1&service=mail&flowName=GlifWebSignIn&flowEntry=ServiceLogin&dsh=S755948691%3A1698770732575372&theme=glif')
    time.sleep(0.1)
    google_account_login(user_info['indeed password'], user_info['indeed email'], driver)

    time.sleep(0.1)


# we can get rid of this but faking typing may be useful
def type_string(elem: WebElement, text: str) -> None:
    random.seed(420)
    for x in text:
        elem.send_keys(x)
        r = random.uniform(0, .1)
        time.sleep(r)
