import discord
from discord.ext import commands
from discord.ext import tasks
import json
import random
from apiclient import discovery
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import numpy as np
import autofarmer
import show_details
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import gspread
# from gspread.models import Cell
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv


# https://hxllmth.jcink.net/index.php?showtopic=1121 # ICEGUIN'S FARM
#  https://hxllmth.jcink.net/index.php?showtopic=1128 #RELU'S FARM
# https://hxllmth.jcink.net/index.php?showtopic=1409 #inferior's farm
# https://hxllmth.jcink.net/index.php?act=ST&f=25&t=1421&st=0#entry7051 # my farm
# https://hxllmth.jcink.net/index.php?showtopic=1417 # boo's farm

##


JSON_NAME = 'users.json'
VALID_STR = "One moment, checking URL validity..."
YOUDONTHAVEAFARM = ", you do not have a registered farm. Please register with: ```f!register MY GOOGLE SPREADSHEET NAME```"

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

tool_list = ["wooden fishing rod", "silver fishing rod", "golden fishing rod", "wooden bug net",
"silver bug net", "golden bug net"]

supplier_mats = ["Thread", "Hide", "Ore", "Wood", "Fish", "Bug", "Fruit", "Herb", "Vegetable", "Grain"]

toolYield = {
    tool_list[0]: "Common Fish",
    tool_list[1]: "Uncommon Fish",
    tool_list[2]: "Rare Fish",
    tool_list[3]: "Common Bug",
    tool_list[4]: "Uncommon Bug",
    tool_list[5]: "Rare Bug"}


# - - - - - - - - - - - - - - - - - - - -


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


async def print_to_channel(msg, ctx):
    await ctx.channel.send(msg)

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
    this_animal = str(this_animal).replace('h2', "")
    if '2' in str(this_animal) and len(all_hearts) < 2:
        num_animals = 2
    elif '3' in str(this_animal) and len(all_hearts) < 3:
        num_animals = 3
        if num_redhearts > 0: num_redhearts=3
    # if num_animals > len(all_hearts) and num_animals < num_redhearts and num_redhearts <=len(all_hearts):
    #     num_redhearts = num_animals #if, say, we have three cows but only one redheart on display, that means all three cows are red
    if "coon" in this_animal:
        print(this_animal, len(all_hearts), "..." , num_animals, num_redhearts)
    # if this_animal
    return num_animals, num_redhearts

def get_per_week(num_animals, num_redhearts, locs):
    per_week = [] #array to hold each animal set's total output per week (assuming 3 posts week)
    nrh = np.copy(num_redhearts)
    for i in range(len(num_animals)):
        if locs[i] == "jackalope":
            nrh[i] = nrh[i]*2
        per_week.append(str(((num_animals[i]*2) + nrh[i])*3))
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
    per_week = get_per_week(num_animals, num_redhearts, locs)
    for i in range(len(animal_names)):
                # sheet.find(animal_names[i])
        if animal_names[i] == "bees" or animal_names[i] == "bee":
            rownum = locs.index("bee house")#+1
        else:
            rownum = locs.index(animal_names[i]) #+1 # row number of the animal we're considering
        new_animal_col[rownum] = [num_animals[i]]
        if animal_names[i] == "raccoon": print(new_redhearts_col[rownum], num_redhearts[i])
        new_redhearts_col[rownum] = [str(num_redhearts[i])]
        if locs[rownum] == "pig" or locs[rownum] == "raccoon":
            new_perweek[rownum] = ["NA"]
        else:
            new_perweek[rownum] = [per_week[i]]
        # print("updating", animal_names[i])
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
        pretty_animal = show_details.strip_animal(this_animal[0])
        if pretty_animal == "orange": pretty_animal = "orange cat"
        elif pretty_animal == "black": pretty_animal = "black cat"
        num_animal, num_hearts = get_num_animals(this_hearts, this_animal[0])
        if pretty_animal == "raccoon":
            print("Animal:", pretty_animal, " no:", num_animal, " no. w/ red hearts:", num_hearts)
        animal_names.append(pretty_animal); num_animals.append(num_animal); num_redhearts.append(num_hearts)
    print(num_redhearts)
    sync_post_to_sheet(animal_names, num_animals, num_redhearts, sheet)  
    return animal_names






############################################################################
########################################################################### END ANIMAL FUNCTIONS
# MISC (TOOLS)
def handle_misc(farm_html, total_locs, product_locs):
    RESULT_STRING = []
    RESULT_STRING.append("**RODS AND NETS** \n")
    count = 0
    for item in tool_list:
        if item in str(farm_html).lower():
            count += 1
            this_roll = random.randint(1, 10)
            prod_index = product_locs.index(toolYield[item]) # index of product we're adding to
            total_locs[prod_index] = int(total_locs[prod_index]) + this_roll
            RESULT_STRING.append(item+", "+toolYield[item]+
            ": **"+str(this_roll)+"**. You now have "+str(total_locs[prod_index]))
    if count == 0:
        RESULT_STRING.append("You have no rods or nets.\n")
    return total_locs, RESULT_STRING


#SUPPLIERS (FROM SHOPS)
def handle_suppliers(farm_html, total_locs, product_locs):
    this_str = "**SUPPLIERS** \n"
    count = 0
    if "t1 supplier" in str(farm_html).lower() or "supplier t1" in str(farm_html).lower():
        roll_result, total_locs = roll_supplier("Common ", total_locs, product_locs)
        this_str += roll_result
        count+=1

    if "t2 supplier" in str(farm_html).lower() or "supplier t2" in str(farm_html).lower():
        roll_result, total_locs = roll_supplier("Uncommon ", total_locs, product_locs)
        this_str += roll_result
        count+=1

    if "t3 supplier" in str(farm_html).lower() or "supplier t3" in str(farm_html).lower():
        roll_result, total_locs = roll_supplier("Rare ", total_locs, product_locs)
        this_str += roll_result
        count+=1
    
    if count == 0:
        return total_locs, "You have **no suppliers** (npcs obtained as shop add-ons).\n"
    else:
        return total_locs, this_str


def roll_supplier(rarity, total_locs, product_locs):
    this_roll = random.randint(1, 5)
    if "Common" in rarity:
        roll_str = "**T1 Supplier**: "
    elif "Uncommon" in rarity:
        roll_str = "**T2 Supplier**: "
    elif "Rare" in rarity:
        roll_str = "**T3 Supplier**: "
    for prod in supplier_mats:
        this_mat = rarity+prod # 'Common + Herb'
        tot_index = product_locs.index(this_mat)
        total_locs[tot_index] = int(total_locs[tot_index]) + int(this_roll)
    roll_str += f"1d5= **{this_roll} {rarity.upper()}** {', '.join(supplier_mats)}\n"
    return roll_str, total_locs




# GET ALL SPREADSHEETS SHARED WITH GOOGLE ACCOUNT
async def obtain_current_sheets():
    global creds
    service = discovery.build('drive', 'v3', credentials=creds)
    stuff = service.files().list(
            pageSize=10, fields="files(name)").execute()
    items = stuff.get('files')
    sheet_names = []
    for n in items: sheet_names.append(n["name"])
    # print(sheet_names)
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
    browser.get(URL)
    time.sleep(5)
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
            return True, vals



async def remind_me(ctx, *args):
    this_usr = ctx.message.author
    user_json = json.load(open(JSON_NAME))
    if len(args) <1:
        await ctx.send(f"The usage for this command is:\n`f!remind on` - turn on ping notifications thursday morning \n`f!remind off` - turn off ping notifications")
    elif args[0].lower() == "off":
        if user_json["user_remind"][str(this_usr.id)] == "Off":
            await ctx.send(f"{this_usr.name}, you have already opted not to be pinged for reminders.")
        else:
            user_json["user_remind"][str(this_usr.id)] = "Off"
            await ctx.send(f"{this_usr.name}, you will no longer be pinged for upkeep post reminders.")
            with open(JSON_NAME, 'w', encoding='utf-8') as f:
                json.dump(user_json, f, ensure_ascii=False, indent=4) # save
    elif args[0].lower() == "on":
        if user_json["user_remind"][str(this_usr.id)] == "On":
            await ctx.send(f"{this_usr.name}, you have already opted into being pinged for reminders.")
        else:
            user_json["user_remind"][str(this_usr.id)] = "On"
            await ctx.send(f"{this_usr.name}, you will now be pinged for upkeep post reminders!")
            with open(JSON_NAME, 'w', encoding='utf-8') as f:
                json.dump(user_json, f, ensure_ascii=False, indent=4) # save



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
    elif sheet_name in user_json["user_sheets"]:
        await ctx.send(
            f"The spreadsheet name **{sheet_name}** is already being used. Please try another.")

    elif this_usr not in user_json["user_sheets"] and sheet_name in current_sheets: # if this user has no farm
        await ctx.send(
        "{}, you are adding the spreadsheet named {}.".format(this_usr.mention, sheet_name))
        await ctx.send("Please copy and paste your farm's **HELLMOUTH** URL now.")
        def check(m):
            return 'hxllmth.jcink.net' in m.content and m.author == ctx.author

        msg = await bot.wait_for("message", check=check)
        await ctx.send(VALID_STR)
        booli, job_elements = await check_valid_URL(msg.content)
        if booli == True:
            user_json["user_sheets"][str(this_usr.id)] = sheet_name
            user_json["user_farmlinks"][str(this_usr.id)] = msg.content
            user_json["user_remind"][str(this_usr.id)] = "False"
            print(user_json)
            sheet = client.open(sheet_name).sheet1
            # job_elements = await selenium_login(msg.content)
            await handle_all_animals(job_elements[0], sheet)
            with open(JSON_NAME, 'w', encoding='utf-8') as f:
                json.dump(user_json, f, ensure_ascii=False, indent=4) # save
            await ctx.send(f"Thank you {this_usr.name}! Your farm is registered and your spreadsheet **{sheet_name}** should now be updated with your farm's data!")
        else:
            await ctx.send(f"{this_usr.name}, that is not a valid link. Please try again.")
 
    elif this_usr not in current_sheets: # if google sheet is not shared yet to email
        await ctx.send(
        "{}, please make sure you correctly shared your spreadsheet titled **{}** with the following email address: \n `autofarming@autofarming.iam.gserviceaccount.com`."
        .format(this_usr.mention, sheet_name))


async def sync_sheet(ctx, *args):
    global bot
    global client
    this_usr = ctx.message.author
    user_json = json.load(open(JSON_NAME))
    if str(this_usr.id) not in user_json["user_sheets"]:
        await ctx.send(f"{this_usr.name}" + YOUDONTHAVEAFARM)
    else:
        await ctx.send(f"Please wait a moment for the web scraper to fetch your farm.")
        sheet_name = user_json["user_sheets"][str(this_usr.id)]
        url = user_json["user_farmlinks"][str(this_usr.id)]
        sheet = client.open(sheet_name).sheet1
        job_elements = await selenium_login(url)
        await handle_all_animals(job_elements[0], sheet)
        await ctx.send(f"{this_usr.name}, your spreadsheet has been successfully updated from your most current farm post!")


async def show_farm(ctx, *args):
    global bot
    global client
    this_usr = ctx.message.author
    user_json = json.load(open(JSON_NAME))
    if str(ctx.message.author.id) not in user_json["user_sheets"]:
        await ctx.send(f"{this_usr.name}" + YOUDONTHAVEAFARM)
    else:
        sheet = client.open(user_json["user_sheets"][str(this_usr.id)]).sheet1
        ani_names = sheet.col_values(1)
        num_anis = sheet.col_values(2)
        prod_names = sheet.col_values(4)
        perweek_vals = sheet.col_values(5)
        if len(args) < 1:
            is_reminding = user_json["user_remind"][str(this_usr.id)]
            # print(len(ani_names), len(num_anis), len(prod_names), len(perweek_vals))
            embed=discord.Embed(title=user_json["user_sheets"][str(this_usr.id)],
                url=user_json["user_farmlinks"][str(this_usr.id)])
            embed.set_thumbnail(url=this_usr.avatar_url)
            embed.set_author(name=f"{this_usr.name}'s weekly farm produce")
            embed.set_footer(text=f"Ping Reminders: {is_reminding}")
            for i in range(1, len(num_anis)): # skip title row
                if int(num_anis[i]) > 0 and ani_names[i] != "pig":
                    embed.add_field(name=f"{prod_names[i]} from {num_anis[i]} {ani_names[i]}", value=str(perweek_vals[i]), inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Please wait a moment while I fetch your farm's page...")
            farm_html = await selenium_login(user_json["user_farmlinks"][str(this_usr.id)])
            if args[0].lower() == 'crop' or args[0].lower() == 'crops':
                embed = show_details.show_crop_info(farm_html[0], sheet,user_json["user_farmlinks"][str(this_usr.id)], this_usr, user_json["user_sheets"][str(this_usr.id)])
                await ctx.send(embed=embed)
            elif args[0].lower() == 'misc' or args[0].lower() == 'tool' or args[0].lower() == 'tools':
                await ctx.send(f"{this_usr.mention}, you have the following tools and special animals:")
                string_response = show_details.show_misc_info(farm_html[0], sheet,user_json["user_farmlinks"][str(this_usr.id)], this_usr, user_json["user_sheets"][str(this_usr.id)])
                await ctx.send(string_response)




async def inventory(ctx, *args):
    global bot
    global client
    this_usr = ctx.message.author
    user_json = json.load(open(JSON_NAME))
    if str(ctx.message.author.id) not in user_json["user_sheets"]:
        await ctx.send(f"{this_usr.name}" + YOUDONTHAVEAFARM)
    else:
        sheet = client.open(user_json["user_sheets"][str(this_usr.id)]).sheet1
        prod_names = sheet.col_values(4)
        total_vals = sheet.col_values(6)
        is_reminding = user_json["user_remind"][str(this_usr.id)]
        embed=discord.Embed(title=user_json["user_sheets"][str(this_usr.id)],
            url=user_json["user_farmlinks"][str(this_usr.id)])
        embed.set_thumbnail(url=this_usr.avatar_url)
        embed.set_author(name=f"{this_usr.name}'s Inventory")
        embed.set_footer(text=f"Ping Reminders: {is_reminding}")
        for i in range(1, len(total_vals)): # skip title row
                if prod_names[i] != "NA" and total_vals[i] != "NA" and total_vals[i] != '0':
                    embed.add_field(name=f"{prod_names[i]}", value=str(total_vals[i]), inline=True)
        await ctx.send(embed=embed)





async def edit_info(ctx, *args):
    global bot
    if len(args) < 1:
        await ctx.send(f"The usage for this command is:\n`f!edit sheet` - to edit name of google spreadsheet \n`f!edit farm` - to change farm link")
    else:
        user_json = json.load(open(JSON_NAME))
        this_usr = ctx.message.author
        if str(this_usr.id) not in user_json["user_sheets"]:
            await ctx.send(f"{this_usr.name}" + YOUDONTHAVEAFARM)
        elif args[0].lower() == 'farm':
            await ctx.send("Please copy and paste your new farm URL now.")
            def check(m):
                return 'hxllmth.jcink.net' in m.content and m.channel == ctx.channel and m.author == ctx.author
            msg = await bot.wait_for("message", check=check)
            await ctx.send(VALID_STR)
            booli, vals = await check_valid_URL(msg.content)
            if booli == True:
                user_json["user_farmlinks"][str(this_usr.id)] = msg.content
                with open(JSON_NAME, 'w', encoding='utf-8') as f:
                    json.dump(user_json, f, ensure_ascii=False, indent=4)
                await ctx.send(f"Your farm link has been updated to `{msg.content}`!")
            else:
                await ctx.send(f"This is not a valid farm link. Try again.")
        elif args[0].lower() == 'sheet':
            await ctx.send("Please copy and paste your new spreadsheet's name now. IT IS CASE-SENSITIVE:")
            def check(m):
                return m.channel == ctx.channel and m.author == ctx.author
            msg = await bot.wait_for("message", check=check)
            current_sheets = await obtain_current_sheets() # get sheets shared with google bot
            if msg.content in current_sheets and msg.content not in user_json["user_sheets"][str(this_usr.id)]:
                old_sheet = user_json["user_sheets"][str(this_usr.id)]
                user_json["user_sheets"][str(this_usr.id)] = msg.content
                with open(JSON_NAME, 'w', encoding='utf-8') as f:
                    json.dump(user_json, f, ensure_ascii=False, indent=4)
                await ctx.send(f"Your sheet's name has been changed from `{old_sheet}` to `{msg.content}`!")
            else:
                await ctx.send(
                    f"Your sheet name was not found as " + 
                    "shared by the the google client. Please make sure you've shared it" + 
                    " with `autofarming@autofarming.iam.gserviceaccount.com`.")

async def roll_items(ctx, *args):
    global bot
    global client
    if len(args) < 1:
        await ctx.send(f"The usage for this command is:\n`f!roll weekly` - roll weekly farm yield \n`f!roll tools` - roll nets and rods after thread completion")
    else:
        user_json = json.load(open(JSON_NAME))
        this_usr = ctx.message.author
        if str(this_usr.id) not in user_json["user_sheets"]:
            await ctx.send(f"{this_usr.name}" + YOUDONTHAVEAFARM)
        elif args[0].lower() == 'tools':
            await ctx.send("Fetching the tools from your farm page...")
            farm_html = await selenium_login(user_json["user_farmlinks"][str(this_usr.id)])
            sheet = client.open(user_json["user_sheets"][str(this_usr.id)]).sheet1
            tool_list = show_details.get_tools(farm_html)
            await ctx.send(tool_list + f"\n {this_usr.name}, to roll for these, type `yes` or `y`:")
            def check(m):
                return m.channel == ctx.channel and m.author == ctx.author
            msg = await bot.wait_for("message", check=check)
            if msg.content.lower() == "yes" or msg.content.lower() == "y":
                prod_names = sheet.col_values(4)
                total_vals = sheet.col_values(6)
                total_locs, result_string = handle_misc(farm_html, total_vals, prod_names)
                total_locs = np.reshape(total_locs, (len(total_locs), 1))
                sheet.update('F:F', total_locs.tolist())
                for result in result_string:
                    await ctx.send(result)
                # await ctx.send(result_string)
            else:
                await ctx.send("Cancelling roll.")
        elif args[0].lower() == 'weekly':
            this_sheet = user_json["user_sheets"][str(this_usr.id)]
            await ctx.send(
            f"{this_usr.mention}, this will collect your farm's information from your FIRST farm post on hellmouth, increment all of your animal produce" +
            f" and execute all crop, tool, and special animal rolls, and" + 
            f" automatically append them to your sheet: \n **{this_sheet}**\n" + 
            f"\nIF YOU ARE BUTCHERING ANIMALS ON YOUR FARM, DELETE THEM FROM YOUR FARM POST *BEFORE* YOU ROLL!\n"
            f"\nAre you sure you want to roll? Type `yes`/`y` or `no`/`n`")
            def check(m):
                return m.channel == ctx.channel and m.author == ctx.author
            msg = await bot.wait_for("message", check=check)
            if msg.content.lower() == "yes" or msg.content.lower() == "y":
                await ctx.send(f"Rolling for {this_usr.name} now...")
                await autofarmer.run_main(this_sheet, user_json["user_farmlinks"][str(this_usr.id)], ctx)
            else:
                await ctx.send(f"Cancelling {this_usr.name}'s roll.")
            
