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
from apiclient import discovery
import asyncio
import botfuncs


hxlogin = json.load(open('hxlogin.json'))
usernameStr = hxlogin['username']
passwordStr = hxlogin['password']

async def get_info(farm_html, sheet):
    await botfuncs.handle_all_animals(farm_html, sheet)
    await farmfunctions.handle_all_crops(farm_html, sheet)



async def run_main(sheet_name):
    URL = "https://hxllmth.jcink.net/index.php?showtopic=1409" #inferior's farm
    job_elements = await botfuncs.selenium_login(URL)
    client = await botfuncs.get_client()
    #Fetch the sheet
    sheet = client.open(sheet_name).sheet1
    python_sheet = sheet.get_all_records()
    # post_count = python_sheet[0]['POSTS']
    # print(post_count)

    # if post_count < len(job_elements)-1: # if the value sitting in our sheet is smaller than the actual num posts made,
    await get_info(job_elements[0], sheet)
    # if datetime.today().weekday() == 6: # IF THE DAY IS SUNDAY
    await farmfunctions.increment_total(sheet)
    # pp = pprint.PrettyPrinter()
    # pp.pprint(python_sheet) # prints google spreadsheet
