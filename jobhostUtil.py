import json
import csv
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
import undetected_chromedriver as uc
from selenium.common.exceptions import NoSuchElementException
import sharedUtil as util
import Applicationsite2 as App2

CHECK_LIST = ["//a[contains(@href,'login')]", "//a[contains(text(),'Apply')]",
              "//*[contains(@class,'apply')]", "//*[contains(text(),'interested')]",
              "//*[contains(text(),'Apply')]"]


def look_for_link(xpath: str, driver: webdriver) -> bool:
    '''
    look for apply button on companies side before we hit a standardized form
    '''
    try:
        t = driver.find_element(By.XPATH, xpath)
        url = driver.current_url
        util.strong_click(t, driver)
        time.sleep(.5)
        if driver.current_url != url or len(driver.find_elements(By.XPATH, "//iframe[@src]")) > 0:
            return True
    except NoSuchElementException:
        pass
    return False


def determine_website2(driver: webdriver, user_info: dict, chatGPT: bool, resume_finetune: bool,
                       current_job: util.JobInfo):
    '''
    checks url to match application templete
    '''
    driver.switch_to.window(driver.window_handles[-1])
    cururl = driver.current_url
    if cururl is None or len(cururl) == 0:
        print("page would not load")
        return None
    time.sleep(1)
    if "greenhouse" in cururl:
        site = App2.Greenhouse(driver, user_info, current_job, chatGPT, resume_finetune)
    elif len(driver.find_elements(By.XPATH, "//iframe[contains(@src,'jobs.ashby')]")) > 0:
        d = driver.find_element(By.XPATH, "//iframe[contains(@src,'jobs.ashby')]")
        driver.switch_to.frame(d)
        site = App2.Ashby(driver, user_info, current_job, chatGPT, resume_finetune)
    elif 'ashby' in cururl:
        site = App2.Ashby(driver, user_info, current_job, chatGPT, resume_finetune)
    elif len(driver.find_elements(By.XPATH, "//iframe[contains(@src,'boards.greenhouse')]")) > 0:
        d = driver.find_element(By.XPATH, "//iframe[contains(@src,'boards.greenhouse.io')]")
        driver.switch_to.frame(d)
        site = App2.Greenhouse(driver, user_info, current_job, chatGPT, resume_finetune)
    elif 'smartrecruiters' in cururl:
        site = App2.SmartRecruiters(driver, user_info, current_job, chatGPT, resume_finetune)
    elif 'paylocity' in cururl:
        site = App2.Paylocity(driver, user_info, current_job, chatGPT, resume_finetune)
    elif "apply.indeed" in cururl:
        site = App2.Indeed(driver, user_info, current_job, chatGPT, resume_finetune)
    elif "jobvite" in cururl:
        site = App2.Jobvite(driver, user_info, current_job, chatGPT, resume_finetune)
    elif "jobjuncture" in cururl:
        site = App2.JobJuncture(driver, user_info, current_job, chatGPT, resume_finetune)
    elif "lever" in cururl:
        site = App2.Lever(driver, user_info, current_job, chatGPT, resume_finetune)
    elif "myworkdayjobs" in cururl:
        site = App2.Workday(driver, user_info, current_job, chatGPT, resume_finetune)
    elif "icims" in cururl:
        site = App2.ICIMS(driver, user_info, current_job, chatGPT, resume_finetune)
    elif "bamboo" in cururl:
        site = App2.Bamboo(driver, user_info, current_job, chatGPT, resume_finetune)
    elif "trinethire" in cururl:
        site = App2.TriNethire(driver, user_info, current_job, chatGPT, resume_finetune)
    else:
        site = None
    return site


def determine_website(driver: webdriver, user_info: dict, chatGPT: bool, resume_finetune: bool,
                      current_job: util.JobInfo, apply: WebElement = None):
    '''
    switch opened tab and identify which application format we have and instantiate class to respond
    '''
    time.sleep(1)
    if apply is not None and apply.get_attribute(
            "aria-label") is not None and "Easy Apply" in apply.get_attribute("aria-label"):
        return App2.LinkedIn(driver, user_info, current_job, chatGPT, resume_finetune)

    site = determine_website2(driver, user_info, chatGPT, resume_finetune, current_job)
    if site is None:
        for x in CHECK_LIST:
            if look_for_link(x, driver):
                site = determine_website2(driver, user_info, chatGPT, resume_finetune, current_job)
                break


    if site is None:
        site = App2.GenericApplicationSite(driver, user_info, current_job, resume_finetune, chatGPT)
    elif "google" in driver.current_url:
        util.google_account_login(info['chatgpt password'], info['chatgpt email'], driver)
    return site


def load(url: str) -> [webdriver, dict, list]:
    with open("user_info\\responses.json", 'r') as file:
        user_info = json.load(file)

    global JOBTITLE_KEYWORDS
    global BADWORDS
    global BADCOMPANY

    JOBTITLE_KEYWORDS = list(map(str.lower, user_info.pop("Job Title must Contain")))
    BADWORDS = list(map(str.lower, user_info.pop("Job Title Keywords to Ignore")))
    BADCOMPANY = list(map(str.lower, user_info.pop("Companies to Ignore")))

    try:
        open("log.txt", "x").close()
    except FileExistsError:
        pass
    with open("log.txt", "r+") as file:
        applied_list = list(csv.reader(file, delimiter=":"))

    options = webdriver.ChromeOptions()
    options.headless = False
    driver = uc.Chrome(options=options, version_main=119, enable_cdp_events=True)
    driver.set_window_size(1100, 800)
    driver.get(url)
    time.sleep(1)
    return driver, user_info, applied_list


def status(applied_list: list, applied: bool, current_job: util.JobInfo, url: str) -> None:
    '''
    writes all jobs seen to log.txt and those applied to applied.txt
    '''
    t = current_job.company + ":" + current_job.title
    if applied:
        with open("applied.txt", "a+") as file:
            file.write(t + '\n')
    else:
        with open("errorlog.txt", "a+") as file:
            file.write(t + ':' + url + '\n')
    with open("log.txt", "a+") as file:
        file.write(t + '\n')
    applied_list.append(t)


def get_description(raw: WebElement) -> list:
    return list(filter(None, raw.text.split("\n")))


def should_apply(current_job: util.JobInfo, applied: list) -> bool:
    ''''''

    if current_job.company.lower() in BADCOMPANY:
        print(current_job.company.lower() + " is in bad companies list")
        return True
    t = [i in current_job.title.lower()
         for i in BADWORDS]
    if any(t):
        print(current_job.title.lower() + " contains " + ', '.join(
            [x for x, y in zip(BADWORDS, t) if y is True]) + " a word we are set to ignore")
        return True
    for x in applied:
        if len(x) > 0 and current_job.company.lower() == x[
            0].lower() and current_job.title.lower() == x[1].lower():
            print(
                "Already applied to " + current_job.company.lower() + " for the role of " + current_job.title.lower())
            return True
    if any(i in current_job.title.lower() for i in JOBTITLE_KEYWORDS):
        return False
    print(current_job.title.lower() + " does not contain any key words")
    return True


def strip_non_ascii(string: str) -> str:
    '''
    Returns the string without non ASCII characters
    '''
    return ''.join((c for c in string if 0 < ord(c) < 127)).strip()
