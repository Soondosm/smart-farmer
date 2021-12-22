import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from html.parser import HTMLParser
import json
import time
import gspread
# from gspread.models import Cell
from oauth2client.service_account import ServiceAccountCredentials
import pprint
import farmfunctions
from datetime import datetime
import asyncio


hxlogin = json.load(open('hxlogin.json'))
usernameStr = hxlogin['username']
passwordStr = hxlogin['password']

async def get_info(farm_html, sheet):
    farmfunctions.handle_all_animals(farm_html, sheet)
    farmfunctions.handle_all_crops(farm_html, sheet)




async def run_main():
    browser = webdriver.Chrome('/Users/soondos/Desktop/independent/itsahardknockendo/chromedriver')
    browser.get(('https://hxllmth.jcink.net/index.php?act=Login&CODE=00'))
    username = browser.find_element_by_name('UserName')
    username.send_keys(usernameStr)
    password = browser.find_element_by_name('PassWord')
    password.send_keys(passwordStr)

    logmein = browser.find_element_by_xpath("//input[@type='submit']")
    logmein.click()

    URL = "https://hxllmth.jcink.net/index.php?showtopic=1121" # ICEGUIN'S FARM
    # URL = "https://hxllmth.jcink.net/index.php?showtopic=1128" #RELU'S FARM
    # URL = "https://hxllmth.jcink.net/index.php?showtopic=1409" #inferior's farm
    # URL = "https://hxllmth.jcink.net/index.php?act=ST&f=25&t=1421&st=0#entry7051" # my farm
    browser.get(URL)
    html = browser.page_source
    time.sleep(2)
    soup = BeautifulSoup(html, features="lxml")
    results = soup.find(id="sascon")
    job_elements = results.find_all("div", class_="post-content")
    # print(results.prettify())
    # print(len(job_elements))
    # print(job_elements[0])
    # for job_element in job_elements:
    #     print(job_element, end="\n"*2)

    #Authorize the API
    scope = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file'
        ]
    file_name = 'client_key.json'
    creds = ServiceAccountCredentials.from_json_keyfile_name(file_name,scope)
    client = gspread.authorize(creds)

    #Fetch the sheet
    sheet = client.open('Flip_AutoFarmSheet').sheet1
    python_sheet = sheet.get_all_records()
    # post_count = python_sheet[0]['POSTS']
    # print(post_count)

    # if post_count < len(job_elements)-1: # if the value sitting in our sheet is smaller than the actual num posts made,
    await get_info(job_elements[0], sheet)
    # if datetime.today().weekday() == 6: # IF THE DAY IS SUNDAY
    await farmfunctions.increment_total(sheet)
    pp = pprint.PrettyPrinter()
    # pp.pprint(python_sheet) # prints google spreadsheet
