from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

import time
import os
import json
import undetected_chromedriver as uc
import sharedUtil
from datetime import date

URL = 'https://chat.openai.com/'
QUESTION_PROMPT = 'Referencing the resume and job description give a detailed answer to this question in the first person. Be casual, personable, warm and inviting. No extra comments. Keep response around 300 words. Do not say based on the job description.'
TASK = "Split the job description into Responsibilities, Requirements and other. Respond with ok."


def startup() -> None:
    '''
    start up and login
    '''
    global driver
    global resume
    global query
    global HEADER
    global FOOTER
    global NAME
    try:
        driver.set_window_size(1000, 1000)
    except:

        options = webdriver.ChromeOptions()
        options.headless = False
        # would like to run in headless mood but get hit with cloudflare
        # options.binary_location = ".\\chrome-win\\chrome.exe"
        # options.set_capability("detach", True)
        with open('user_info\\query.json', 'r') as file:
            query = json.loads(file.read())
        with open('user_info\\responses.json', 'r') as file:
            info = json.load(file)
        with open('user_info\\start up.json', 'r') as file:
            resume = json.loads(file.read())
        NAME = info['name']

        HEADER = info['name'] + '\n' + info['address'] + '\n' + info['what is your current location'] + ' ' + info['zip'] + '\n' + info['email'] + '\n' + info[
            'phone'] + '\n' + str(date.today().strftime('%b, %d')) + '\n\n'

        driver = uc.Chrome(options=options, version_main=119, enable_cdp_events=True)

        driver.set_window_size(1000, 1000)
        driver.get(URL)

        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//div[text() = 'Log in']"))).click()
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-provider = 'google']"))).click()
        time.sleep(.1)
        sharedUtil.google_account_login(info['chatgpt password'], info['chatgpt email'], driver)
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Okay')]"))).click()
        except:
            pass


def ask_question(crystal_ball, message: str) -> str:
    '''
    wait for chat gpt to add a new response line and return the text
    '''
    text_ref = "//div[contains(@class,'markdown prose w-full break-words dark:prose-invert dark')]"

    crystal_ball.send_keys(message)
    time.sleep(.1)
    crystal_ball.send_keys(Keys.ENTER)
    count = len(driver.find_elements(By.XPATH, text_ref))
    text = ''
    while count >= len(driver.find_elements(By.XPATH, text_ref)) or text != driver.find_elements(By.XPATH, text_ref)[-1].text:
        if len(driver.find_elements(By.XPATH, text_ref)) > 0:
            text = driver.find_elements(By.XPATH, text_ref)[-1].text
        time.sleep(1)

    return driver.find_elements(By.XPATH, text_ref)[-1].text


def format_coverletter(res: str, current_job) -> str:
    '''
    makes response from chat gpt look like a cover letter
    '''
    res = res.replace('\n', '\n\n')
    if "Dear" in res:
        res = res[res.index("Dear"):]
    if NAME in res:
        res = res[:res.index(NAME) + len(NAME)]
    while '[' in res:
        res = res[:res.index('[')] + res[res.index(']') + 1:]
    res = HEADER + 'Hiring Team \n' + current_job.company + '\n' + current_job.location + '\n\n' + res
    return res


def answer(question: str, current_job, as_file: bool) -> str:
    '''
    answers question using chat gpt referencing the description and the user's resume
    '''
    startup()

    time.sleep(.1)
    crystal_ball = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//textarea[@id = 'prompt-textarea']")))
    ask_question(crystal_ball, json.dumps(resume))
    job_processing = {'Task': TASK,
                      'Company': current_job.company,
                      'Title': current_job.title,
                      'Location': current_job.location,
                      'Description': current_job.description
                      }
    ask_question(crystal_ball, json.dumps(job_processing))
    if question.lower() == 'cover letter':
        res = format_coverletter(ask_question(crystal_ball, json.dumps(query)), current_job)
    else:
        res = ask_question(crystal_ball, QUESTION_PROMPT + question)

    if as_file:
        with open(os.getcwd() + "\\user_info\\" + "cover-letter.txt", "w") as file:
            file.write(res)
    return res


def write_coverletter(current_job) -> str:
    return answer("cover letter", current_job, True)


if __name__ == "__main__":
    temp = "As a fast-growing startup, Motionworks is looking for new or recent graduates at the intersection of data engineering and data science with demonstrated interest in urban planning or transport analytics. We want people with a passion for data modeling, software development, and applying your trade to make the world a better place. You will be tasked with: Implementing data pipelines built in Apache Airflow on the Google Cloud Platform (Google Composer) Building mathematical/machine learning models that sit on top of our primary products Improving data processes to reduce pipeline processing costs and increase efficiency of existing workflows Identifying and implementing data structures, storage, and indexing to optimize existing pipelines and/or reduce pipeline processing costs Working with product leads to operationalize research and development concepts into repeatable and efficient data pipelines Implementing quality control checks in the data pipeline Designing, prototyping, and developing innovative data solutions for geospatial problems Analyzing transportation data patterns to ensure our products accurately reflect current conditions Improving, validating, documenting, and performing analytics work on our current data solutions An ideal candidate for this position will be a solid developer who thinks about the physical world in which people move. These attributes are combined to critically analyze a problem at hand, do research on viable and effective solutions, perform modeling work, implement solutions, and analytically assess the results. You will need to communicate complex concepts and solutions to technical and nontechnical audiences through effective visualizations, statistical analysis, and documentation. We expect you to be organized yet scrappy, thoughtful, and most importantly, have a strong desire to learn. Required Qualifications and Skills Masters in Mathematics, Physics, Computer Science, analytical City Planning, or Geography (or equivalent degree) or Bachelors in similar with 2+ years of experience in quantitative analytics, data science, or data engineering. Demonstrated development in Python Understanding of cloud computing (preferably AWS or GCP) Demonstrated SQL experience in at least one of the following: BigQuery, RedShift, or Snowflake Proven experience working with geospatial data (e.g., geojson, shapefiles) Experience with version control (preferably Git/GitHub) Experience with Linux/Unix command line Ability to build/test statistical and/or machine learning model Ability to create effective visualizations in at least one of the following: Tableau, Matplotlib, or ggplot Solid critical thinking, problem-solving, and communication skills "
    job = sharedUtil.JobInfo(temp, "Data Engineer", 'motionworks', 'San Diego, CA')
    write_coverletter(job)
