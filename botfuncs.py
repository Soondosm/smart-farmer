import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext import tasks
import json
from apiclient import discovery
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import numpy as np
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import gspread
# from gspread.models import Cell
from oauth2client.service_account import ServiceAccountCredentials

JSON_NAME = 'users.json'

hxlogin = json.load(open('hxlogin.json'))
usernameStr = hxlogin['username']
passwordStr = hxlogin['password']

user_json = json.load(open('users.json'))
isActive = False
msg_content = None
channel = None
creds = None
bot = None
client = None

async def get_client():
    return client

async def set_creds(new_creds):
    global creds
    creds = new_creds

async def set_bot(new_bot):
    global bot
    bot = new_bot

async def set_channel(new_channel):
    global channel
    channel = new_channel


async def print_to_channel(msg):
    await channel.send(msg)

async def triggerTrue(state):
    global isActive
    isActive = state

async def edit_msg_content(content):
    global msg_content
    msg_content = content


def getTrigger():
    return isActive

async def getContent():
    return msg_content

async def initialize_client():
    global client
    #Authorize the API
    scope = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file'
        ]
    file_name = 'client_key.json'
    creds = ServiceAccountCredentials.from_json_keyfile_name(file_name,scope)
    await set_creds(creds)
    new_client = gspread.authorize(creds)
    client = new_client

############################################################################
########################## ANIMAL FUNCTIONS ########################################
############################################################################

def strip_animal(this_animal):
    this_animal = re.sub('<[^<]+?>', '', str(this_animal))
    # print(this_animal)
    this_animal = re.sub(r"[\([{})\]]", '', str(this_animal))
    # print(this_animal)
    this_animal = re.split(';|!| |, |\*|\n', str(this_animal))
    # print(this_animal)
    while '' in this_animal:
        this_animal.remove('')
    index = 0
    # for s in this_animal[index]:
    if this_animal[index][0].isdigit():
        index +=1
    this_animal = this_animal = this_animal[index].lower()
    # print(this_animal)
    return this_animal


def get_num_redhearts(all_hearts):
    heart_count = 0
    for heart in all_hearts:
        if 'red' in str(heart) or  'rgb(255, 0, 0)' in str(heart):
            heart_count+=1
    return heart_count

def get_num_animals(this_hearts, this_animal):
    all_hearts = this_hearts[0].find_all('i')
    num_animals = len(all_hearts)
    num_redhearts = get_num_redhearts(all_hearts)
    this_animal = str(this_animal).replace('2', "")
    if '2' in str(this_animal) and len(all_hearts) < 2:
        num_animals = 2
    elif '3' in str(this_animal) and len(all_hearts) < 3:
        num_animals = 3
    # print("num animals: ", len(all_hearts), "num red: ", num_redhearts)
    return num_animals, num_redhearts

def get_per_week(num_animals, num_redhearts):
    per_week = [] #array to hold each animal set's total output per week (assuming 3 posts week)
    for i in range(len(num_animals)):
        per_week.append(((num_animals[i]*2) + num_redhearts[i])*3)
    return per_week

def sync_post_to_sheet(animal_names, num_animals, num_redhearts, sheet):
    locs = sheet.col_values(1)
    animal_num_col = sheet.col_values(2)
    new_animal_col = np.full(len(animal_num_col), '0', dtype=object); new_animal_col[0] = animal_num_col[0]
    new_animal_col = np.reshape(new_animal_col, (len(new_animal_col), 1))
    animal_num_col = np.reshape(animal_num_col, (len(animal_num_col), 1))
    animal_redhearts_col = sheet.col_values(3)
    new_redhearts_col = np.full(len(animal_redhearts_col), '0', dtype=object); new_redhearts_col[0] = animal_redhearts_col[0]
    new_redhearts_col = np.reshape(new_redhearts_col, (len(new_redhearts_col), 1))
    animal_redhearts_col = np.reshape(animal_redhearts_col, (len(animal_redhearts_col), 1))
    perweek_col = sheet.col_values(5)
    new_perweek = np.full(len(perweek_col), '0', dtype=object); new_perweek[0] = perweek_col[0]
    new_perweek = np.reshape(new_perweek, (len(new_perweek), 1))
    perweek_col = np.reshape(perweek_col, (len(perweek_col), 1))
    per_week = get_per_week(num_animals, num_redhearts)
    for i in range(len(animal_names)):
                # sheet.find(animal_names[i])
        if animal_names[i] == "bees" or animal_names[i] == "bee":
            rownum = locs.index("bee house")#+1
        else:
            rownum = locs.index(animal_names[i]) #+1 # row number of the animal we're considering
        new_animal_col[rownum] = [num_animals[i]]
        new_redhearts_col[rownum] = [str(num_redhearts[i])]
        if locs[rownum] == "pig" or locs[rownum] == "raccoon":
            new_perweek[rownum] = ["NA"]
        else:
            new_perweek[rownum] = [per_week[i]]
        print("updating", animal_names[i])
    sheet.update('B:B', new_animal_col.tolist()) #DATA MUST BE PRESENTED AS 2D ARRAY
    sheet.update('C:C', new_redhearts_col.tolist())
    sheet.update('E:E', new_perweek.tolist())


async def handle_all_animals(farm_html, sheet):
    all_animal_html = farm_html.find_all("div", class_="ranching")
    # print("TELL: ", all_animal_html)
    with_hearts = [] # span tag, allows us to check how many "red" there is
    num_animals = [] # number of animals present on farm
    num_redhearts = [] # number of animals with red hearts
    animal_names = [] # prettified animal name
    for aminal in all_animal_html:
        with_hearts.append(aminal.find_all('span'))
        # animal_names.append(strip_animal(aminal.find_all('h2')))
        # animal_names.append(aminal.find_all('h2'))
        this_hearts = aminal.find_all('span')
        this_animal = aminal.find_all('h2')
        # print(this_animal)
        pretty_animal = strip_animal(this_animal[0])
        num_animal, num_hearts = get_num_animals(this_hearts, this_animal[0])
        # print("Animal:", pretty_animal, " no:", num_animal, " no. w/ red hearts:", num_hearts)
        animal_names.append(pretty_animal); num_animals.append(num_animal); num_redhearts.append(num_hearts)
    sync_post_to_sheet(animal_names, num_animals, num_redhearts, sheet)  
    return animal_names

############################################################################
########################################################################### END ANIMAL FUNCTIONS



# GET ALL SPREADSHEETS SHARED WITH GOOGLE ACCOUNT
async def obtain_current_sheets():
    global creds
    service = discovery.build('drive', 'v3', credentials=creds)
    stuff = service.files().list(
            pageSize=10, fields="files(name)").execute()
    items = stuff.get('files')
    sheet_names = []
    for n in items: sheet_names.append(n["name"])
    print(sheet_names)
    return sheet_names


# LOG INTO HXLLMTH
async def selenium_login(URL):
    browser = webdriver.Chrome('./chromedriver')
    browser.get(('https://hxllmth.jcink.net/index.php?act=Login&CODE=00'))
    username = browser.find_element_by_name('UserName')
    username.send_keys(usernameStr)
    password = browser.find_element_by_name('PassWord')
    password.send_keys(passwordStr)
    logmein = browser.find_element_by_xpath("//input[@type='submit']")
    logmein.click()
    # URL = "https://hxllmth.jcink.net/index.php?showtopic=1121" # ICEGUIN'S FARM
    # URL = "https://hxllmth.jcink.net/index.php?showtopic=1128" #RELU'S FARM
    # URL = "https://hxllmth.jcink.net/index.php?showtopic=1409" #inferior's farm
    # URL = "https://hxllmth.jcink.net/index.php?act=ST&f=25&t=1421&st=0#entry7051" # my farm
    # URL = "https://hxllmth.jcink.net/index.php?showtopic=1417" # boo's farm
    browser.get(URL)
    time.sleep(2)
    html = browser.page_source
    soup = BeautifulSoup(html, features="lxml")
    results = soup.find(id="sascon")
    job_elements = results.find_all("div", class_="post-content")
    return job_elements


async def check_valid_URL(url):
    vals = await selenium_login(url)
    if len(vals) == 0:
        return False
    elif len(vals)>0:
        all_crop_html = vals[0].find_all("div", class_="farming")
        all_animal_html = vals[0].find_all("div", class_="ranching")
        if len(all_crop_html) or len(all_animal_html) > 0:
            return True

async def register_new(ctx, *args):
    global bot
    this_usr = ctx.message.author
    current_sheets = await obtain_current_sheets()
    user_json = json.load(open(JSON_NAME))
    sheet_name = ' '.join(args)
    if str(this_usr.id) in user_json["user_sheets"]: # if user's farm is already kept track of
        print(type(this_usr.id), this_usr.id)
        await ctx.send(
        '{}, you have already registered your farm: **{}**.'.format(this_usr.mention, user_json["user_sheets"][str(this_usr.id)]))

    elif this_usr not in user_json["user_sheets"] and sheet_name in current_sheets: # if this user has no farm
        await ctx.send(
        "{}, you are adding the spreadsheet named {}.".format(this_usr.mention, sheet_name))
        await ctx.send("Please copy and paste your farm's URL now.")
        def check(m):
            return 'hxllmth.jcink.net' in m.content and m.channel == channel and m.author == ctx.author

        msg = await bot.wait_for("message", check=check)
        await ctx.send("One moment, checking URL validity...")
        if await check_valid_URL(msg.content) == True:
            user_json["user_sheets"][this_usr.id] = sheet_name
            user_json["user_farmlinks"][this_usr.id] = msg.content
            print(user_json)
            sheet = client.open(sheet_name).sheet1
            job_elements = await selenium_login(msg.content)
            await handle_all_animals(job_elements[0], sheet)
            with open(JSON_NAME, 'w', encoding='utf-8') as f:
                json.dump(user_json, f, ensure_ascii=False, indent=4) # save
            await ctx.send(f"Thank you {this_usr.nick}! Your farm is registered and your spreadsheet **{sheet_name}** should now be updated with your farm's data!")
        else:
            await ctx.send(f"{this_usr.nick}, that is not a valid link. Please try again.")
 
    elif this_usr not in current_sheets: # if google sheet is not shared yet to email
        await ctx.send(
        "{}, please make sure you correctly shared your spreadsheet titled **{}** with the following email address: \n `autofarming@autofarming.iam.gserviceaccount.com`."
        .format(this_usr.mention, sheet_name))

async def show_farm(ctx, *args):
    print()

async def edit_info(ctx, *args):
    global bot
    this_usr = ctx.message.author
    if str(this_usr.id) not in 

    print()
