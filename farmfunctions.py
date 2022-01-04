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
import discord

# RESULT_STRING = []

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
                "black cat":"Common Bug",
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

penguinMatching = {
    1:"Common Ore",
    2:"Uncommon Ore",
    3:"Rare Ore"
}

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

do_not_auto_add = ["pig", "raccoon", "jackalope","penguin"]


async def handle_all_crops(farm_html, sheet):
    RESULT_STRING = []
    all_crop_html = farm_html.find_all("div", class_="farming")
    total_locs = sheet.col_values(6)
    product_locs = sheet.col_values(4)
    is_cloak = 0
    total_locs, strings_to_add = botfuncs.handle_misc(farm_html, total_locs, product_locs)
    for string in strings_to_add: RESULT_STRING.append(string)
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
        total_locs[prod_index], RESULT_STRING = await roll_crop(product_name, crop_name, crop_count, is_cloak, total_locs[prod_index], RESULT_STRING)
    total_locs = np.reshape(total_locs, (len(total_locs), 1))
    sheet.update('F:F', total_locs.tolist())
    return RESULT_STRING

async def roll_crop(product_name, crop_name, crop_count, is_cloak, total, RESULT_STRING):
    rarity = product_name.split(" ")[0]
    max_range = rarityCropYield[rarity]
    result_str = "\n\n\n\nRolling " + str(crop_count) + " " + crop_name 
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
    return new_total, RESULT_STRING



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

async def get_penguin(sheet, RESULT_STRING):
    locs = sheet.col_values(1)
    penguin_row = locs.index("penguin")+1
    num_penroll = int(sheet.cell(penguin_row, 2).value) + int(sheet.cell(penguin_row, 3).value) #num animal +
    if num_penroll == 0:
        RESULT_STRING.append("You have no penguins. Sadder than not having raccoons.")
    else:
        num_penroll = num_penroll * 3
        mat_names = sheet.col_values(4)
        curr_total = sheet.col_values(6)
        curr_total = np.reshape(curr_total, (len(curr_total), 1))
        result_str = "\n\n\n\n**PENGUINS**\n"
        for i in range(num_penroll):
            result = random.randint(1, 3)
            chosen_mat = penguinMatching[result]
            mat_index = mat_names.index(chosen_mat)
            # print("BEFORE", chosen_mat, curr_total[mat_index], type(curr_total[mat_index]))
            curr_total[mat_index] = [(int(curr_total[mat_index])+2)]
            print("PINGIN", i, chosen_mat, curr_total[mat_index])
            result_str += "Penguin " + str(i+1) + " yield is " + str(result) + "/3: 2 " + chosen_mat + " -> " + str(curr_total[mat_index][0]) + "\n"
            # await botfuncs.edit_msg_content(result_str)
        RESULT_STRING.append(result_str) # add to discord output
        # await botfuncs.triggerTrue(True) #permit bot to go
        sheet.update('F:F', curr_total.tolist())
    return RESULT_STRING


async def get_raccoon(sheet, RESULT_STRING):
    locs = sheet.col_values(1) # get all animal names
    raccoon_row = locs.index("raccoon")+1
    num_racroll = int(sheet.cell(raccoon_row, 2).value) + int(sheet.cell(raccoon_row, 3).value) #num animal + num animals with red hearts
    # print("RICKROLLS", num_racroll)
    if num_racroll == 0:
        RESULT_STRING.append("You have no raccoons. Sad.")
    else:
        num_racroll = num_racroll * 3 #accounting for 3 posts
        mat_names = sheet.col_values(4)
        curr_total = sheet.col_values(6)
        curr_total = np.reshape(curr_total, (len(curr_total), 1))
        result_str = "\n\n\n\n**RACCOONS\n**"
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
            result_str += "Raccoon " +str(i+1)+" yield is " + str(result) + "/8: " + chosen_mat + " -> " + str(curr_total[mat_index][0]) + "\n"
            # await botfuncs.edit_msg_content(result_str)
        RESULT_STRING.append(result_str) # add to discord output
        # await botfuncs.triggerTrue(True) #permit bot to go
        sheet.update('F:F', curr_total.tolist())
    return RESULT_STRING


async def display_to_discord(RESULT_STRING):
    # print(len(RESULT_STRING), RESULT_STRING)
    for str in RESULT_STRING:
       await botfuncs.print_to_channel(str)
    RESULT_STRING = [] # reset
    # await botfuncs.edit_msg_content(RESULT_STRING)
    # await botfuncs.triggerTrue(True)

async def increment_total(sheet, ctx, URL, RESULT_STRING):
    week_locs = sheet.col_values(5) #GETS PER WEEK COLUMN VALUES
    total_locs = sheet.col_values(6) # GET RUNNING TOTAL SO FAR
    aniname_locs = sheet.col_values(1)
    prodname_locs = sheet.col_values(4)
    unc_jewel = None
    unc_ingot = None
    print(len(aniname_locs), aniname_locs)
    # newcol =  np.full(len(week_locs), '0', dtype=object); newcol[0] = tp[0]
    for i in range(1, len(week_locs)):
        # if i < len(aniname_locs):
        # print(aniname_locs[i], week_locs[i])
        if aniname_locs[i] == "jackalope":
            unc_jewel = prodname_locs.index("Uncommon Jewel")
            unc_ingot = prodname_locs.index("Uncommon Ingot")
            print("NUMBER OF JACKALOPES:", week_locs[i])
            total_locs[unc_jewel] = int(int(week_locs[i])/2+int(total_locs[unc_jewel]))
            total_locs[unc_ingot] = int(int(week_locs[i])/2+int(total_locs[unc_ingot]))
            total_locs[i] = "NA"
        elif (aniname_locs[i] == "raccoon" or aniname_locs[i] == "pig" 
        or aniname_locs[i] == "penguin"):
            total_locs[i] = "NA"
        else:
            total_locs[i] = int(int(week_locs[i])+int(total_locs[i]))
            # print(aniname_locs[i], week_locs[i], int(week_locs[i])+int(total_locs[i]))
    total_locs = np.reshape(total_locs, (len(total_locs), 1))
    sheet.update('F:F', total_locs.tolist())
    # UPDATE STRING 

    embed=discord.Embed(title=f"{ctx.message.author.nick}'s farm", url=URL, color=0x3eb300)
    embed.set_author(name="THIS WEEK'S ANIMAL PRODUCE")

    # RESULT_STRING.append("\nThis week, your animals have produced the following: ")

    # result_str = "This week, your animals have produced the following: \n"

    aniname_locs.pop(0) # REMOVE COLUMN TITLE, 'ANIMAL NAME'
    for ani in aniname_locs:
        if ani in AnimalToMat and ani not in do_not_auto_add:
            index = prodname_locs.index(AnimalToMat[ani])
            week_val = week_locs[index]
            total_val = total_locs[index]
            if int(week_val) > 0: # if no animals are producing this week, ignore

                embed.add_field(name=(ani), value=(AnimalToMat[ani] + " - " + str(week_val)  
                + " -> \n" + str(total_val[0])), inline=True)

                # RESULT_STRING.append(ani + " - " + AnimalToMat[ani] + " - **" + str(week_val)  
                # + "** -> **" + str(total_val[0]) + "** \n")

                # result_str+= (ani + " - " + AnimalToMat[ani] + " - **" + str(week_val)  
                # + "** -> **" + str(total_val[0]) + "** \n")

        elif ani == "jackalope":
            temp_locs = sheet.col_values(6) # GET RUNNING TOTAL SO FAR
            val = int(int(week_val)/2)
            # print(unc_ingot, unc_jewel)
            # print(total_locs[unc_jewel], "STUFF", temp_locs[unc_ingot])

            embed.add_field(name=ani, value=("Unc. Ingot - " + str(val) + " -> " +
            str(temp_locs[unc_ingot]) + "\nUnc. Jewel - " + str(val) + " -> " + 
            str(temp_locs[unc_jewel])), inline=True)

            # RESULT_STRING.append(f"{ani} - **{str(val)}** Uncommon Ingot, **{str(val)} Uncommon Jewel, totaling {str(total_locs[unc_ingot][0])} and {temp_locs[unc_jewel][0]}")
            
            # result_str += f"{ani} - **{str(val)}** Uncommon Ingot, **{str(val)} Uncommon Jewel, totaling {str(total_locs[unc_ingot])} and {total_locs[unc_jewel]}"
    
    RESULT_STRING = await get_raccoon(sheet, RESULT_STRING)
    RESULT_STRING = await get_penguin(sheet, RESULT_STRING)
    # botfuncs.print_embed(result_str)
    # RESULT_STRING.append(result_str)
    await display_to_discord(RESULT_STRING)
    await ctx.send(embed=embed)

