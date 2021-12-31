from bs4 import BeautifulSoup
import numpy as np
import re
import gspread
# from gspread.models import Cell
from oauth2client.service_account import ServiceAccountCredentials
import random
import numpy as np
# import farmbot #import discord bot companion functionality
import botfuncs
import time

RESULT_STRING = []

AnimalToMat = {"sheep": "Common Thread", 
                "fox": "Uncommon Thread",
                "silkworm": "Rare Thread",
                "cow":"Milk",
                "chicken":"Egg",
                "shrew":"Common Jewel",
                "groundhog":"Uncommon Jewel",
                "rabbit":"Rare Jewel",
                "hedgehog":"Common Ingot",
                "porcupine":"Uncommon Ingot",
                "echidna":"Rare Ingot",
                "squirrel":"Common Wood",
                "woodpecker":"Uncommon Wood",
                "beaver":"Rare Wood",
                "lizard":"Common Leather",
                "snake":"Uncommon Leather",
                "crocodile":"Rare Leather",
                "orange cat":"Common Fish",
                "black cat":"Common Bugs",
                "raccoon":"random",
                "bee house":"Honeycomb" }
MatToMath = {"Common Thread":0,
            "Uncommon Thread":0,
            "Rare Thread":0,
            "Milk":0,
            "Egg":0,
            "Common Jewel":0,
            "Uncommon Jewel":0,
            "Rare Jewel":0,
            "Common Ingot":0,
            "Uncommon Ingot":0,
            "Rare Ingot":0,
            "Common Wood":0 }

raccoonMatching = {
    1:"Common Herb",
    2:"Common Vegetable",
    3:"Common Fruit",
    4:"Common Grain",
    5:"Common Ore",
    6:"Common Wood",
    7:"Common Bug",
    8:"Common Thread"}

cropMatching = {
    "apple":"Common Fruit",
    "grape":"Uncommon Fruit",
    "pumpkins":"Uncommon Fruit",
    "cranberry":"Rare Fruit",
    "beet":"Common Vegetable",
    "bok choy":"Uncommon Vegetable",
    "rhubarb":"Rare Vegetable",
    "wheat":"Common Grain",
    "corn":"Uncommon Grain",
    "amaranth":"Rare Grain",
    "garlic":"Common Herb",
    "hops":"Uncommon Herb",
    "tea leaf":"Rare Herb"}

rarityCropYield = {
    "Common":10,
    "Uncommon":10,
    "Rare":5,
    "Epic":3}

tool_list = ["wooden fishing rod", "silver fishing rod", "golden fishing rod", "wooden bug net",
"silver bug net", "golden bug net"]
toolYield = {
    tool_list[0]: "Common Fish",
    tool_list[1]: "Uncommon Fish",
    tool_list[2]: "Rare Fish",
    tool_list[3]: "Common Bug",
    tool_list[4]: "Uncommon Bug",
    tool_list[5]: "Rare Bug"}


async def handle_all_crops(farm_html, sheet):
    all_crop_html = farm_html.find_all("div", class_="farming")
    total_locs = sheet.col_values(6)
    product_locs = sheet.col_values(4)
    is_cloak = 0
    total_locs = handle_misc(farm_html, total_locs, product_locs)
    if "harvest cloak" in str(farm_html).lower():
        print("WE HAVE A CLOAAAKKKK")
        is_cloak = 1
    for crop in all_crop_html:
        crop = crop.find_all('h2')
        crop_name = botfuncs.strip_animal(crop)
        if crop_name == "tea":
            crop_name += " leaf"
        elif crop_name == "bok":
            crop_name += " choy"
        crop_count = get_crop_count(str(crop[0]))
        # print("found", crop_count, crop_name, "&", is_cloak, "harvest cloak")
        product_name = cropMatching[crop_name]
        prod_index = product_locs.index(product_name)
        print(product_name, prod_index)
        total_locs[prod_index] = await roll_crop(product_name, crop_name, crop_count, is_cloak, total_locs[prod_index])
    total_locs = np.reshape(total_locs, (len(total_locs), 1))
    sheet.update('F:F', total_locs.tolist())

def handle_misc(farm_html, total_locs, product_locs):
    RESULT_STRING.append("Rolling rods and nets: \n")
    count = 0
    for item in tool_list:
        if item in str(farm_html).lower():
            count += 1
            this_roll = random.randint(1, 10)
            prod_index = product_locs.index(toolYield[item]) # index of product we're adding to
            total_locs[prod_index] = int(total_locs[prod_index]) + this_roll
            RESULT_STRING.append(item+", "+toolYield[item]+
            ":\n**"+str(this_roll)+"**. You now have "+str(total_locs[prod_index]))
    if count == 0:
        RESULT_STRING.append("You have no rods or nets.\n")
    return total_locs

async def roll_crop(product_name, crop_name, crop_count, is_cloak, total):
    rarity = product_name.split(" ")[0]
    max_range = rarityCropYield[rarity]
    result_str = "Rolling " + str(crop_count) + " " + crop_name 
    if is_cloak == 1:
        result_str += " + " + str(crop_count)
    result_str += ":\n"
    final_val = 0
    roll_set = []
    for i in range(crop_count):
        this_roll = random.randint(1, max_range)
        roll_set.append(this_roll)
        final_val += this_roll
    roll_set.sort(reverse=True)
    new_total = int(final_val) + int(total)
    result_str += '`' + str(roll_set)+'`'+ "\n= **" + str(final_val) + " " + crop_name + "** " + ". You now have " + str(new_total)
    RESULT_STRING.append(result_str)
    # await botfuncs.edit_msg_content(result_str)
    # await botfuncs.triggerTrue(True) #permit bot to go
    return new_total



def get_crop_count(this_crop):
    # print(this_crop)
    this_crop = re.sub('<h2>', '', this_crop)
    this_crop = re.sub('</h2>', '', this_crop)
    this_crop = re.sub(r"[\([{})\]]", '', str(this_crop))
    # print(this_crop)
    num = []
    for s in this_crop:
        if s.isdigit():
            num.append(s)
    return int("".join(num))



async def get_raccoon(sheet):
    locs = sheet.col_values(1) # get all animal names
    raccoon_row = locs.index("raccoon")+1
    num_racroll = int(sheet.cell(raccoon_row, 2).value) + int(sheet.cell(raccoon_row, 3).value) #num animal +
    # print("RICKROLLS", num_racroll)
    if num_racroll == 0:
        RESULT_STRING.append("You have no raccoons. Sad.")
    else:
        mat_names = sheet.col_values(4)
        curr_total = sheet.col_values(6)
        curr_total = np.reshape(curr_total, (len(curr_total), 1))
        result_str = ""
        for i in range(num_racroll):
            result = random.randint(1, 8)
            chosen_mat = raccoonMatching[result]
            mat_index = mat_names.index(chosen_mat)
            # print("BEFORE", chosen_mat, curr_total[mat_index], type(curr_total[mat_index]))
            curr_total[mat_index] = [(int(curr_total[mat_index])+1)]
            print("RACCOON", i, chosen_mat, curr_total[mat_index])
            num_place = ""
            if i+1 == 1: 
                num_place = "st"
            elif i+1 == 2:
                num_place = "nd"
            elif i+1 == 3:
                num_place = "rd"
            else: num_place = "th"
            result_str += "User, your " + str(i+1)+num_place+ " raccoon yield is " + str(result) + "/8: " + chosen_mat + ". You now have " + str(curr_total[mat_index][0]) + "\n"
            # await botfuncs.edit_msg_content(result_str)
        RESULT_STRING.append(result_str) # add to discord output
        # await botfuncs.triggerTrue(True) #permit bot to go
        sheet.update('F:F', curr_total.tolist())


async def display_to_discord():
    # print(len(RESULT_STRING), RESULT_STRING)
    for str in RESULT_STRING:
       await botfuncs.print_to_channel(str)
    # await botfuncs.edit_msg_content(RESULT_STRING)
    # await botfuncs.triggerTrue(True)

async def increment_total(sheet):
    week_locs = sheet.col_values(5) #GETS PER WEEK COLUMN VALUES
    total_locs = sheet.col_values(6) # GET RUNNING TOTAL SO FAR
    aniname_locs = sheet.col_values(1)
    prodname_locs = sheet.col_values(4)
    print(len(aniname_locs), aniname_locs)
    # newcol =  np.full(len(week_locs), '0', dtype=object); newcol[0] = tp[0]
    for i in range(1, len(week_locs)):
        # if i < len(aniname_locs):
        # print(aniname_locs[i], week_locs[i])
        if aniname_locs[i] == "raccoon" or aniname_locs[i] == "pig":
            total_locs[i] = "NA"
        else:
            total_locs[i] = (int(week_locs[i])+int(total_locs[i]))
            # print(aniname_locs[i], week_locs[i], int(week_locs[i])+int(total_locs[i]))
    total_locs = np.reshape(total_locs, (len(total_locs), 1))
    sheet.update('F:F', total_locs.tolist())
    # UPDATE STRING 
    result_str = "This week, your animals have produced the following: \n"
    # print(aniname_locs)
    # while '' in aniname_locs:
    #     aniname_locs.remove('')
    # while ' ' in aniname_locs:
    #     aniname_locs.remove(' ')
    aniname_locs.pop(0) # REMOVE COLUMN TITLE, 'ANIMAL NAME'
    # print(aniname_locs)
    for ani in aniname_locs:
        if ani in AnimalToMat and ani != "pig" and ani != "raccoon":
            index = prodname_locs.index(AnimalToMat[ani])
            # index = week_locs.index(mat)
            week_val = week_locs[index]
            total_val = total_locs[index]
            if int(week_val) > 0: # if no animals are producing this week, ignore
                result_str+= (ani + " - " + AnimalToMat[ani] + " - **" + str(week_val)  
                + "** totaling **" + str(total_val[0]) + "** \n")
    await get_raccoon(sheet)
    RESULT_STRING.append(result_str)
    await display_to_discord()

