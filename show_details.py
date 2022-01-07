from bs4 import BeautifulSoup
import numpy as np
import re
import gspread
# from gspread.models import Cell
from oauth2client.service_account import ServiceAccountCredentials
import nltk
nltk.download('omw-1.4')
from nltk.stem import WordNetLemmatizer
import random
import numpy as np
# import farmbot #import discord bot companion functionality
import botfuncs
import time
import discord
import json
import farmfunctions

tool_list = ["wooden fishing rod", "silver fishing rod", "golden fishing rod", "wooden bug net",
"silver bug net", "golden bug net"]
toolYield = {
    tool_list[0]: "Common Fish",
    tool_list[1]: "Uncommon Fish",
    tool_list[2]: "Rare Fish",
    tool_list[3]: "Common Bug",
    tool_list[4]: "Uncommon Bug",
    tool_list[5]: "Rare Bug"}

rarityCropYield = {
    "Common":10,
    "Uncommon":10,
    "Rare":5,
    "Epic":3}

raccoonMatching = {
    1:"Common Herb",
    2:"Common Vegetable",
    3:"Common Fruit",
    4:"Common Grain",
    5:"Common Ore",
    6:"Common Wood",
    7:"Common Bug",
    8:"Common Thread"}

penguinMatching = {
    1:"Common Ore",
    2:"Uncommon Ore",
    3:"Rare Ore"
}



def show_crop_info(farm_html, sheet, url,this_usr, sheet_name):
    wnl = WordNetLemmatizer()
    all_crop_html = farm_html.find_all("div", class_="farming")
    total_locs = sheet.col_values(6)
    product_locs = sheet.col_values(4)
    is_cloak = 0
    is_cloak_str = ""
    if "harvest cloak" in str(farm_html).lower():
        print("WE HAVE A CLOAAAKKKK")
        is_cloak = 1
    # RESULT_STRING.append("\n**CROPS**")
    embed=discord.Embed(title=sheet_name,  url=url)
    embed.set_thumbnail(url=this_usr.avatar_url)
    embed.set_author(name=f"{this_usr.name}'s crops")
    for crop in all_crop_html:
        crop = crop.find_all('h2')
        crop_name = strip_animal(crop)
        if crop_name == "tea":
            crop_name += " leaf"
        elif crop_name == "bok":
            crop_name += " choy"
        crop_count = farmfunctions.get_crop_count(str(crop[0]))
        product_name = farmfunctions.cropMatching[wnl.lemmatize(crop_name, 'n')]
        # print("found", crop_count, crop_name, wnl.lemmatize(crop_name, 'n'), "&", is_cloak, "harvest cloak")
        prod_index = product_locs.index(product_name)
        # print(product_name, prod_index)
        rarity = product_name.split(" ")[0]
        if is_cloak == 1:
            is_cloak_str = f" + {crop_count} (harvest cloak)"
        embed.add_field(name=f"{crop_count} {crop_name}", value=f"{product_name}: {crop_count}d{rarityCropYield[rarity]}{is_cloak_str}", inline=False)
    return embed

def show_misc_info(farm_html, sheet, url, this_usr, sheet_name):
    this_str = ""
    locs = sheet.col_values(1) # get all animal names
    raccoon_row = locs.index("raccoon")+1
    num_racroll = (int(sheet.cell(raccoon_row, 2).value) + int(sheet.cell(raccoon_row, 3).value)) * 3 #num animal + num animals with red hearts
    penguin_row = locs.index("penguin")+1
    num_penroll = ((int(sheet.cell(penguin_row, 2).value) + int(sheet.cell(penguin_row, 3).value))*2) * 3 #num animal +
    if "harvest cloak" in str(farm_html).lower():
        this_str += "You have a *harvest cloak*! For each seed planted, you will yield one additional harvest.\n"
    if "t1 supplier" in str(farm_html).lower() or "supplier t1" in str(farm_html).lower():
        this_str += "**T1 Supplier** - obtain 1d5 common materials.\n"
    if "t2 supplier" in str(farm_html).lower() or "supplier t2" in str(farm_html).lower():
        this_str += "**T2 Supplier** - obtain 1d5 uncommon materials.\n"
    if "t3 supplier" in str(farm_html).lower() or "supplier t3" in str(farm_html).lower():
        this_str += "**T3 Supplier** - obtain 1d5 rare materials.\n"
    this_str += get_tools(farm_html)
    if num_racroll > 0:
        print(int(sheet.cell(raccoon_row, 2).value), int(sheet.cell(raccoon_row, 3).value))
        this_str += "You will get " + str(num_racroll) + " **raccoon** products of common rarity (herb, vegetable, fruit, grain, ore, wood, bug, thread.).\n"
    if num_penroll > 0:
        this_str += "You will get " + str(num_penroll) + " **penguin** ores of different possible rarities (common, uncommon, rare). \n"

    return this_str



def get_tools(farm_html):
    str_of_tools = "**You have the following tools:** \n"
    for i in range(len(tool_list)):
        if tool_list[i] in str(farm_html).lower():
            str_of_tools += "1d10 **" + toolYield[tool_list[i]] + "** from " + tool_list[i] + "\n"
    return str_of_tools


# STRIP STUFF AWAY FROM ANIMALS AND CROPS
def strip_animal(this_animal):
    this_animal = re.sub('<[^<]+?>', '', str(this_animal))
    this_animal = re.sub(r"[\([{})\]]", '', str(this_animal))
    this_animal = re.split(';|!| |, |\*|\n', str(this_animal))
    while '' in this_animal:
        this_animal.remove('')
    index = 0
    # for s in this_animal[index]:
    if this_animal[index][0].isdigit():
        index +=1
    this_animal = this_animal = this_animal[index].lower()
    # print(this_animal)
    return this_animal
