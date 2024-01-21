from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webelement import WebElement
import time
import os
import re
import json
import traceback
from datetime import date
import bigQuestion as bQ
import appUtil
import sharedUtil as util
from resume_finetune import summarize_job

DEBUG = True
# app.trinthire.com
# recruiting.ultipro.com w/ login
# rippling
# ADP
# ICIMS captcha detection?
# successfactors w/login
'''in testing'''


def Generic_Apply(driver: webdriver, user_info: dict) -> None:
    driver.find_element(By.XPATH,
                        "//input[contains(@id,'FIRST')] | //input[contains(@id,'First')] | //input[contains(@id,'first')]").send_keys(
        user_info["first name"])
    driver.find_element(By.XPATH,
                        "//input[contains(@id,'LAST')] | //input[contains(@id,'Last')] | //input[contains(@id,'last')]").send_keys(
        user_info["last name"])
    driver.find_element(By.XPATH,
                        "//input[contains(@id,'EMAIL')] | //input[contains(@id,'Email')] | //input[contains(@id,'email')]").send_keys(
        user_info["email"])

    util.strong_click(driver.find_element(By.XPATH,
                                          "//*[contains(text(),'APPLY')] | //*[contains(text(),'Apply')] | //*[contains(text(),'apply')] |"
                                          "//*[contains(text(),'SUBMIT')] | //*[contains(text(),'Submit')] | //*[contains(text(),'submit')]"),
                      driver)
    return None


class GenericApplicationSite:
    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool,
                 resume_finetune: bool):
        self.driver, self.user_info, self.current_job, self.chatGPT, self.resume_finetune = driver, user_info, current_job, chatGPT, resume_finetune
        self.element, self.submit, self.next = None, None, None

    def name(self) -> str:
        return 'Generic App'

    def login(self):
        pass

    def error_exit(self):
        '''
        stops infinite loop
        '''
        raise Exception("caught in infinite loop exiting")

    def question_cycle2(self, index=0):
        time.sleep(.5)
        t = self.driver.find_elements(By.XPATH, self.element)

        for x in range(index, len(t)):
            try:
                appUtil.question_process(t[x], self.user_info, self.driver, self.current_job,self.chatGPT)
            except StaleElementReferenceException:
                t = self.driver.find_elements(By.XPATH, self.element)
                appUtil.question_process(t[x], self.user_info, self.driver, self.current_job,
                                         self.chatGPT)
            except Exception:
                print("error answering question")
                if DEBUG:
                    traceback.print_exc()

            # reload elem and try again

    def question_cycle(self) -> bool:
        time.sleep(1)
        appUtil.send_files(self.driver, self.current_job, self.user_info, self.chatGPT,
                           self.resume_finetune)
        time.sleep(5)
        if self.element is None:
            '''
            true generic
            '''
            self.element = "//input/ancestor::div/child::div[text() and not(contains(text(),'pply'))]/parent::div"
            self.submit = "//*[contains(text(),'APPLY')] | //*[contains(text(),'Apply')] | //*[contains(text(),'apply')] |//*[contains(text(),'SUBMIT')] | " \
                          "//*[contains(text(),'Submit')] | //*[contains(text(),'submit')]"

        if self.next is None:
            # will crash here if element = None and will stop apply to job
            self.question_cycle2()

        else:
            count = 0
            while len(self.driver.find_elements(By.XPATH, self.submit)) == 0:
                count += 1
                if count > 10:
                    self.error_exit()
                self.question_cycle2()
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, self.next))).click()
                time.sleep(2)

        util.strong_click(self.driver.find_element(By.XPATH, self.submit), self.driver)
        time.sleep(1)
        if len(self.driver.find_elements(By.XPATH, self.submit)) == 0:
            self.driver.close()
            try:
                self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass
            return True
        try:
            self.driver.switch_to.window(self.driver.window_handles[0])
        except:
            pass
        return False


# needs work still detect as bot
class SmartRecruiters(GenericApplicationSite):
    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool,
                 resume_finetune: bool):
        super().__init__(driver, user_info, current_job, chatGPT, resume_finetune)
        self.next = "//button[text()='Next']"
        self.element = "//*[@class='hydrated'] | //div[contains(@data-test,'personal-info-')] | //*[@data-test='consent']"
        self.submit = "//button[text()='Submit']"
        self.login()

    def name(self) -> str:
        return 'Smart Recruiters'

    def login(self):
        time.sleep(.5)
        try:
            self.driver.find_element(By.XPATH, "//a[@id='st-apply']").click()
        except:
            pass


class LinkedIn(GenericApplicationSite):
    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool,
                 resume_finetune: bool):
        super().__init__(driver, user_info, current_job, chatGPT, resume_finetune)
        self.element = "//div[contains(@class ,'jobs-easy-apply-form-section__grouping')]"
        self.submit = "//button[@aria-label='Submit application']"
        self.next = "//button[@aria-label='Continue to next step'] | //button[@aria-label='Review your application'] | " \
                    "//button[@aria-label='Submit application']"

    def name(self) -> str:
        return 'LinkedIn Easy Apply'

    def error_exit(self):
        WebDriverWait(self.driver, 1).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Dismiss']"))).click()
        WebDriverWait(self.driver, 1).until(
            EC.element_to_be_clickable((By.XPATH,
                                        "//button[@data-control-name='discard_application_confirm_btn']"))).click()
        print("error exit")

    def question_cycle(self) -> bool:
        count = 0
        sent_files = False
        while len(self.driver.find_elements(By.XPATH, self.submit)) == 0:
            count += 1
            if not sent_files and len(
                    self.driver.find_elements(By.XPATH, "//input[@type='file']")) > 0:
                sent_files = appUtil.send_files(self.driver, self.current_job, self.user_info,
                                                self.chatGPT, self.resume_finetune)

            if count > 10:
                self.error_exit()
            self.question_cycle2()
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, self.next))).click()
            time.sleep(2)
        util.strong_click(self.driver.find_element(By.XPATH, self.submit), self.driver)
        time.sleep(1)
        appUtil.popup_remove(self.driver)
        return True


class Workday(GenericApplicationSite):
    '''


    '''

    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool,
                 resume_finetune: bool):
        super().__init__(driver, user_info, current_job, chatGPT, resume_finetune)
        # self.element = "//*[@required]/parent::*"
        self.element = "//abbr[text()='*']/ancestor::div[contains(@data-automation-id,'formField-')]"
        self.submit = "//button[text()='Submit']"
        self.next = "//button[contains(text(),'Continue') or contains(text(),'Next')]"
        try:
            with open("user_info\\start up.json") as file:
                self.resume_info = json.loads(file.read())
        except:
            self.resume_info = None
        self.login()

    def name(self) -> str:
        return 'Workday'

    def login(self):
        try:
            WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//a[text()='Apply']"))).click()
            WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[@data-automation-id='autofillWithResume']"))).click()
        except TimeoutException:
            pass

        time.sleep(2)
        # login
        try:
            WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@aria-required='true']")))
            login = self.driver.find_elements(By.XPATH, "//input[@aria-required='true']")
            login[0].send_keys(self.user_info["workday email"])
            login[1].send_keys(self.user_info["workday password"])

            util.strong_click(self.driver.find_element(By.XPATH, "//button[text()='Sign In']"),
                              self.driver)
        except TimeoutException:
            pass
        time.sleep(1)

    def question_cycle(self) -> bool:
        time.sleep(5)
        progress_bar = self.driver.find_element(By.XPATH,
                                                "//div[@data-automation-id='progressBar']").text.split(
            "\n")

        def date_entry(input, base):
            date = input.split("/")
            base.find_element(By.XPATH,
                              ".//input[@aria-label='Month']").send_keys(
                date[0])
            base.find_element(By.XPATH,
                              ".//input[@aria-label='Year']").send_keys(
                date[1])

        for section in progress_bar:
            # load takes to long need better solution
            time.sleep(8)
            if section == "My Experience":
                if self.resume_info is not None:
                    for job in self.resume_info["work experience"]:
                        WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH,
                                                        "//button[@aria-label='Add Work Experience'] | //button[@aria-label='Add Another Work Experience']"))).click()
                        time.sleep(.5)
                        base = self.driver.find_elements(By.XPATH, "//fieldset")[-1]
                        appUtil.textbox(base.find_element(By.XPATH,
                                                          ".//input[@data-automation-id='jobTitle']"),
                                        job["job title"])
                        appUtil.textbox(base.find_element(By.XPATH,
                                                          ".//input[@data-automation-id='company']"),
                                        job["company"])

                        date_entry(job["start"], base.find_element(By.XPATH,
                                                                   ".//div[@data-automation-id='formField-startDate']"))
                        date_entry(job["end"], base.find_element(By.XPATH,
                                                                 ".//div[@data-automation-id='formField-endDate']"))
                        appUtil.textbox(base.find_element(By.XPATH,
                                                          ".//textarea[@data-automation-id='description']"),
                                        "\n".join(job["duties"]))

                    for job in self.resume_info["education"]:
                        util.strong_click(
                            self.driver.find_element(By.XPATH,
                                                     "//button[@aria-label='Add Education'] | //button[@aria-label='Add Another Education']"),
                            self.driver)
                        time.sleep(.5)
                        base = self.driver.find_elements(By.XPATH, "//fieldset")[-1]
                        appUtil.textbox(base.find_element(By.XPATH,
                                                          ".//input[@data-automation-id='school']"),
                                        job["school"])
                        appUtil.combobox(base.find_element(By.XPATH,
                                                           ".//input[@data-automation-id='degree']"),
                                         job["degree"],
                                         self.driver)

                        appUtil.textbox(base.find_element(By.XPATH,
                                                          ".//input[@data-automation-id='gpa']"),
                                        job["gpa"])

                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, self.next))).click()
                pass
            elif section == "Autofill with Resume":

                appUtil.send_files(self.driver, self.current_job, self.user_info, self.chatGPT,
                                   self.resume_finetune)
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, self.next))).click()
            elif section == "Review":
                util.strong_click(self.driver.find_element(By.XPATH, self.submit), self.driver)
                time.sleep(1)
                if len(self.driver.find_elements(By.XPATH, self.submit)) == 0:
                    self.driver.close()
                    return True
                self.driver.switch_to.window(self.driver.window_handles[0])
                return False
            else:
                self.question_cycle2()
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, self.next))).click()


class Indeed(GenericApplicationSite):

    # manually fill this on out
    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool,
                 resume_finetune: bool):
        super().__init__(driver, user_info, current_job, chatGPT, resume_finetune)

    '''
    since indeed has a standard application format we just interface with it directly
    '''

    def name(self) -> str:
        return 'Indeed'

    def question_cycle(self) -> bool:
        continue_button = "//button[contains(@class,'-continue')]"
        self.driver.switch_to.window(self.driver.window_handles[-1])

        try:
            appUtil.textbox(WebDriverWait(self.driver, 1).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@id='input-firstName']"))),
                self.user_info["first name"])
            appUtil.textbox(self.driver.find_element(By.XPATH, "//input[@id='input-lastName']"),
                            self.user_info["last name"])
            try:
                appUtil.textbox(
                    self.driver.find_element(By.XPATH, "//input[@id='input-phoneNumber']"),
                    self.user_info["phone"])
            except NoSuchElementException:
                pass
            try:
                appUtil.textbox(self.driver.find_element(By.XPATH, "//input[@id='input-email']"),
                                self.user_info["email"])
            except NoSuchElementException:
                pass
            self.driver.find_element(By.XPATH,
                                     continue_button).click()
        except TimeoutException:
            pass

        try:
            self.driver.find_element(By.XPATH,
                                     "//h1[contains(text(),'Review')]")
            self.driver.find_element(By.XPATH,
                                     continue_button).click()
        except NoSuchElementException:
            pass
        time.sleep(1)
        try:
            self.driver.find_element(By.XPATH,
                                     "//div[starts-with(@aria-controls,'resume-display')]").click()
            # appUtil.send_files(self.driver, self.current_job, self.user_info, self.chatGPT,
            #                   self.resume_finetune)
            # time.sleep(1)
        except NoSuchElementException:
            # self.driver.find_element(By.XPATH,
            # "//div[@aria-controls='resume-display-content']").click()
            pass
        appUtil.send_files(self.driver, self.current_job, self.user_info, self.chatGPT,
                           self.resume_finetune)
        time.sleep(1)
        try:
            self.driver.find_element(By.XPATH, "//span[text()='Use original file']").click()
        except NoSuchElementException:
            pass
        WebDriverWait(self.driver, 1).until(
            EC.element_to_be_clickable(
                (By.XPATH, continue_button))).click()

        time.sleep(1)
        count = 0
        while len(self.driver.find_elements(By.XPATH,
                                            "//h1[contains(text(),'uestions from the employer')]")) > 0 and count < 10:
            count += 1
            q = self.driver.find_elements(By.XPATH,
                                          "//div[starts-with(@class,'ia-Questions-item')]")
            for x in q:
                appUtil.question_process(x, self.user_info, self.driver, self.current_job,
                                         self.chatGPT)
            WebDriverWait(self.driver, 1).until(
                EC.element_to_be_clickable(
                    (By.XPATH, continue_button))).click()
            time.sleep(1)

        if len(self.driver.find_elements(By.XPATH,
                                         "//h1[text()='The employer is looking for these qualifications']")) > 0:
            WebDriverWait(self.driver, 1).until(
                EC.element_to_be_clickable(
                    (By.XPATH, continue_button))).click()

        try:
            appUtil.textbox(self.driver.find_element(By.XPATH, "//input[@id='jobTitle']"),
                            self.user_info["last job title"])
            self.driver.find_element(By.XPATH, "//input[@id='jobTitle']").send_keys(Keys.ESCAPE)
            appUtil.textbox(self.driver.find_element(By.XPATH, "//input[@id='companyName']"),
                            self.user_info["last job company"])
            self.driver.find_element(By.XPATH, "//input[@id='companyName']").send_keys(Keys.ESCAPE)
            WebDriverWait(self.driver, 1).until(
                EC.element_to_be_clickable(
                    (By.XPATH, continue_button))).click()
        except NoSuchElementException:
            pass

        time.sleep(3)
        self.driver.find_element(By.XPATH,
                                 continue_button).click()
        time.sleep(1)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        return True


class Jobvite(GenericApplicationSite):
    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool,
                 resume_finetune: bool):
        super().__init__(driver, user_info, current_job, chatGPT, resume_finetune)
        self.element = ".//*[@aria-required='true']"
        self.submit = "//button[@aria-label='Send Application']"
        self.next = "//button[@aria-label='Next']"

    def name(self) -> str:
        return 'Jobvite'


class Greenhouse(GenericApplicationSite):
    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool,
                 resume_finetune: bool):
        super().__init__(driver, user_info, current_job, chatGPT, resume_finetune)
        self.element = "//div[@class='field']"
        self.submit = "//input[@id='submit_app']"
        if self.current_job is None:
            self.getinfo()
    def name(self) -> str:
        return 'Greenhouse'

    def getinfo(self):
        job_descrip = summarize_job(self.driver.find_element(By.XPATH, "//div[@id='content']").text)
        job_title = self.driver.find_element(By.XPATH, "//h1[@class='app-title']").text
        company = self.driver.find_element(By.XPATH, "//span[@class='company-name']").text
        location = self.driver.find_element(By.XPATH, "//div[@class='location']").text
        self.current_job = util.JobInfo(job_descrip, job_title, company, location)


class Lever(GenericApplicationSite):
    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool,
                 resume_finetune: bool):
        super().__init__(driver, user_info, current_job, chatGPT, resume_finetune)
        self.element = "//li[@class='application-question custom-question'] | //div[@class='application-additional']"
        self.submit = "//button[text()='Submit application']"
        if self.current_job is None:
            self.getinfo()
        self.login()

    def login(self):
        # move to login if you encouter this
        try:
            WebDriverWait(self.driver, .5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[text()='Apply for this job']"))).click()
        except NoSuchElementException:
            pass

    def name(self) -> str:
        return 'Lever'

    def getinfo(self):
        cat = self.driver.find_elements(By.XPATH, "//div[@class='posting-categories']/div")
        job_descrip = summarize_job(self.driver.find_element(By.XPATH, "//div[@class='section-wrapper page-full-width']").text)
        job_title = self.driver.find_element(By.XPATH, "//div[@class='posting-headline']/h2").text
        #workaround
        company =self.driver.current_url.split('/')[3]

        location = cat[0].text

        self.current_job = util.JobInfo(job_descrip, job_title, company, location)


class JobJuncture(GenericApplicationSite):

    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool,
                 resume_finetune: bool):
        super().__init__(driver, user_info, current_job, chatGPT, resume_finetune)

    def question_cycle(self):
        self.driver.find_element(By.XPATH, "//a[contains(text(),'Apply')]").click()
        time.sleep(1)
        self.driver.find_element(By.XPATH, "//input[@name='fullname']").send_keys(
            self.user_info["first name"] + " " + self.user_info["last name"])
        self.driver.find_element(By.XPATH, "//input[@name='email']").send_keys(
            self.user_info["email"])
        self.driver.find_element(By.XPATH, "//input[@name='subscribe']").click()
        self.driver.find_element(By.XPATH, "//input[@name='topresume']").click()

        appUtil.send_files(self.driver, self.current_job, self.user_info, self.resume_finetune)

        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.driver.close()
        self.driver.switch_to.window(driver.window_handles[0])
        return True

    def name(self) -> str:
        return 'JobJuncture'


class ICIMS(GenericApplicationSite):
    '''

    '''

    # TODO: 2nd page has problems find elements xpath is correct
    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool,
                 resume_finetune: bool):
        super().__init__(driver, user_info, current_job, chatGPT, resume_finetune)
        self.element = "//div[contains(@class,'iCIMS_FieldRow_Inline') and not(@style)] | //div[@class='iCIMS_TableRow ']"
        self.submit = "//input[@type='submit']"
        self.next = "//input[@type='submit']"
        self.login()

    def name(self) -> str:
        return 'ICIMS'

    def login(self):
        self.driver.switch_to.frame(
            self.driver.find_element(By.XPATH, "//iframe[@id='icims_content_iframe']"))
        try:
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    self.driver.find_element(By.XPATH,
                                             "//a[@title = 'Apply for this job online']"))).click()
            time.sleep(1)
        except NoSuchElementException:
            pass
        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable(
                self.driver.find_element(By.XPATH, "//input[@type = 'email']"))).send_keys(
            self.user_info["icims email"])
        try:
            self.driver.find_element(By.XPATH, "//input[@type = 'checkbox']").click()
        except NoSuchElementException:
            pass
        self.driver.find_element(By.XPATH, "//input[@value = 'Next']").click()
        time.sleep(1)
        try:
            self.driver.switch_to.default_content()
            time.sleep(.5)
            self.driver.find_element(By.XPATH, "//input[@type = 'password']").send_keys(
                self.user_info["icims password"])
            time.sleep(.5)
            # hidden element causing problems i do not like this solution
            self.driver.find_elements(By.XPATH, "//button[@type = 'submit']")[1].click()
        except NoSuchElementException:
            pass


class Ashby(GenericApplicationSite):
    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool,
                 resume_finetune: bool):
        super().__init__(driver, user_info, current_job, chatGPT, resume_finetune)
        self.element = "//div[contains(@class,'ashby-application-form-field')] | //fieldset[contains(@class,'fieldEntry')]"
        self.submit = "//button[contains(@class,'submit')]"
        self.login()

    def login(self):
        try:
            WebDriverWait(self.driver, .5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[text()='Apply for this Job']"))).click()
            d = self.driver.find_element(By.XPATH, "//iframe[contains(@src,'jobs.ashby')]")
            self.driver.switch_to.frame(d)
        except (NoSuchElementException, TimeoutException):
            pass

    def name(self) -> str:
        return 'Ashby'


# needs more testing
class Paylocity(GenericApplicationSite):
    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool,
                 resume_finetune: bool):
        super().__init__(driver, user_info, current_job, chatGPT, resume_finetune)
        self.element = "//div[contains(@class,'form-group')]"
        self.submit = "//button[@id='btn-submit']"
        self.next = "//button[@id='btn-submit']"
        self.login()

    def name(self) -> str:
        return 'Paylocity'

    def login(self):
        try:
            WebDriverWait(self.driver, .5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[text()='Apply']"))).click()
        except TimeoutException:
            pass

    def question_cycle(self):
        appUtil.send_files(self.driver, self.current_job, self.user_info, self.chatGPT,
                           self.resume_finetune)
        time.sleep(2)
        appUtil.textbox(WebDriverWait(self.driver, .5).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='info.firstName']"))),
            self.user_info["first name"])

        appUtil.textbox(self.driver.find_element(By.XPATH, "//input[@id='info.lastName']"),
                        self.user_info["last name"])
        appUtil.textbox(self.driver.find_element(By.XPATH, "//input[@id='info.email']"),
                        "test" + self.user_info["email"])
        appUtil.textbox(self.driver.find_element(By.XPATH, "//input[@id='info.cellPhone']"),
                        self.user_info["phone"])

        appUtil.combobox(self.driver.find_element(By.XPATH, "//div[@id='info.smsOptedIn']"), "yes",
                         self.driver)
        appUtil.combobox(self.driver.find_element(By.XPATH, "//div[@id='info.desiredSalaryType']"),
                         "yearly", self.driver)
        appUtil.numberbox(
            self.driver.find_element(By.XPATH, "//input[@id='info.minimumDesiredSalary']"),
            self.user_info["salary"])
        appUtil.numberbox(
            self.driver.find_element(By.XPATH, "//input[@id='info.maximumDesiredSalary']"),
            str(int(self.user_info["salary"]) * 1.2))

        util.strong_click(self.driver.find_element(By.XPATH, self.next), self.driver)
        count = 0
        while len(self.driver.find_elements(By.XPATH, self.submit)) == 0:
            count += 1
            if count > 10:
                self.error_exit()
            self.question_cycle2()
            next = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, self.next)))
            util.strong_click(next, self.driver)
            time.sleep(2)
        if len(self.driver.find_elements(By.XPATH, self.submit)) == 0:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            return True
        self.driver.switch_to.window(self.driver.window_handles[0])
        return False


# needs work
class Bamboo(GenericApplicationSite):
    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool,
                 resume_finetune: bool):
        super().__init__(driver, user_info, current_job, chatGPT, resume_finetune)
        self.element = "//*[contains(@class,'CandidateField ')]"
        self.submit = "//span[text()='Submit Application']"
        self.login()

    def name(self) -> str:
        return 'Bamboo'

    def login(self):
        try:
            # i hate this solution
            time.sleep(.5)
            elem = self.driver.find_elements(By.XPATH,
                                             "//button//span[text()='Apply for This Job']")
            elem[2].click()
        except TimeoutException:
            pass


class TriNethire(GenericApplicationSite):
    def __init__(self, driver: webdriver, user_info: dict, current_job: util.JobInfo, chatGPT: bool,
                 resume_finetune: bool):
        super().__init__(driver, user_info, current_job, chatGPT, resume_finetune)
        self.element = "//div[contains(@class,'form-group')]"
        self.submit = "//input[@type='submit']"

    def name(self) -> str:
        return 'TriNet hire'
