import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext import tasks
import json
from apiclient import discovery
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


hxlogin = json.load(open('hxlogin.json'))
usernameStr = hxlogin['username']
passwordStr = hxlogin['password']

user_json = json.load(open('users.json'))
isActive = False
msg_content = None
channel = None
creds = None
bot = None

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
    sheet_name = ' '.join(args)
    if this_usr in user_json["user_sheets"]: # if user's farm is already kept track of
        await ctx.send(
        '{}, you have already registered your farm: {}.'.format(this_usr.mention, user_json["user_sheets"][this_usr]))

    if this_usr not in user_json["user_sheets"] and sheet_name in current_sheets: # if this user has no farm
        await ctx.send(
        "{}, you are adding the spreadsheet named {}.".format(this_usr.mention, sheet_name))
        await ctx.send("Please copy and paste your farm's URL now.")
        def check(m):
            return 'hxllmth.jcink.net' in m.content and m.channel == channel and m.author == ctx.author

        msg = await bot.wait_for("message", check=check)
        await ctx.send("One moment, checking for URL validity...")
        if await check_valid_URL(msg.content) == True:
            user_json["user_sheets"][this_usr] = sheet_name
            user_json["user_farmlinks"][this_usr] = msg.content
            print(user_json)
            await ctx.send(f"Thank you {this_usr.nick}! Your farm is registered and your spreadsheet **{sheet_name}** should now be updated with your farm's data!")
        else:
            await ctx.send(f"{this_usr.nick}, that is not a valid link. Please try again.")
 
    elif this_usr not in current_sheets: # if google sheet is not shared yet to email
        await ctx.send(
        "{}, please make sure you correctly shared your spreadsheet titled **{}** with the following email address: \n `autofarming@autofarming.iam.gserviceaccount.com`."
        .format(this_usr.mention, sheet_name))