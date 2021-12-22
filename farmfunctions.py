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
                "bee house":"Honeycomb"            }
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
    8:"Common Thread"
}

cropMatching = {
    "apple":"Common Fruit",
    "grape":"Uncommon Fruit",
    "pumpkin":"Uncommon Fruit",
    "cranberry":"Rare Fruit",
    "beet":"Common Vegetable",
    "bok choy":"Uncommon Vegetable",
    "rhubarb":"Rare Vegetable",
    "wheat":"Common Grain",
    "corn":"Uncommon Grain",
    "amaranth":"Rare Grain",
    "garlic":"Common Herb",
    "hops":"Uncommon Herb",
    "tea leaf":"Rare Herb"
}

rarityYield = {
    "Common":10,
    "Uncommon":10,
    "Rare":5,
    "Epic":3
}

def get_num_redhearts(all_hearts):
    heart_count = 0
    for heart in all_hearts:
        if 'red' in str(heart):
            heart_count+=1
        # print(heart, "\n")
    return heart_count


def handle_all_crops(farm_html, sheet):
    all_crop_html = farm_html.find_all("div", class_="farming")
    is_cloak = 0
    if "harvest cloak" in str(farm_html).lower():
        print("WE HAVE A CLOAAAKKKK")
        is_cloak = 1
    for crop in all_crop_html:
        crop = crop.find_all('h2')
        crop_name = strip_animal(crop)
        crop_count = get_crop_count(str(crop[0]))
        print("found", crop_count, crop_name, "&", is_cloak, "harvest cloak")


def handle_all_animals(farm_html, sheet):
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


def get_num_animals(this_hearts, this_animal):
    all_hearts = this_hearts[0].find_all('i')
    num_animals = len(all_hearts)
    # print("\n \n SEPARATED HEARTS: ", len(all_hearts), all_hearts, "\n")
    num_redhearts = get_num_redhearts(all_hearts)
    this_animal = str(this_animal).replace('2', "")
    if '2' in str(this_animal) and len(all_hearts) < 2:
        num_animals = 2
    elif '3' in str(this_animal) and len(all_hearts) < 3:
        num_animals = 3
    # print("num animals: ", len(all_hearts), "num red: ", num_redhearts)
    return num_animals, num_redhearts


def strip_animal(this_animal):
    this_animal = re.sub('<[^<]+?>', '', str(this_animal))
    # print(this_animal)
    this_animal = re.sub(r"[\([{})\]]", '', str(this_animal))
    # print(this_animal)
    this_animal = re.split(';|!| |, |\*|\n', str(this_animal))
    # print(this_animal)
    while '' in this_animal:
        this_animal.remove('')
    # print(this_animal)
    this_animal = this_animal = this_animal[0].lower()
    # print(this_animal)
    return this_animal

def sync_post_to_sheet(animal_names, num_animals, num_redhearts, sheet):
    locs = sheet.col_values(1)
    animal_num_col = sheet.col_values(2)
    animal_num_col = np.reshape(animal_num_col, (len(animal_num_col), 1))
    animal_redhearts_col = sheet.col_values(3)
    animal_redhearts_col = np.reshape(animal_redhearts_col, (len(animal_redhearts_col), 1))
    perweek_col = sheet.col_values(5)
    perweek_col = np.reshape(perweek_col, (len(perweek_col), 1))
    per_week = get_per_week(num_animals, num_redhearts)
    for i in range(len(animal_names)):
                # sheet.find(animal_names[i])
        if animal_names[i] == "bees" or animal_names[i] == "bee":
            rownum = locs.index("bee house")#+1
        else:
            rownum = locs.index(animal_names[i]) #+1 # row number of the animal we're considering
        animal_num_col[rownum] = [num_animals[i]]
        animal_redhearts_col[rownum] = [str(num_redhearts[i])]
        perweek_col[rownum] = [per_week[i]]
        # sheet.update_cell(rownum, 2, str(num_animals[i]))
        # sheet.update_cell(rownum, 3, num_redhearts[i])
        # sheet.update_cell(rownum, 5, per_week[i])
        print("updating", animal_names[i])
    sheet.update('B:B', animal_num_col.tolist()) #DATA MUST BE PRESENTED AS 2D ARRAY
    sheet.update('C:C', animal_redhearts_col.tolist())
    sheet.update('E:E', perweek_col.tolist())


async def get_raccoon(sheet):
    locs = sheet.col_values(1) # get all animal names
    raccoon_row = locs.index("raccoon")+1
    num_racroll = int(sheet.cell(raccoon_row, 2).value) + int(sheet.cell(raccoon_row, 3).value) #num animal +
    print("RICKROLLS", num_racroll)
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
        await botfuncs.edit_msg_content(result_str)
    await botfuncs.triggerTrue(True) #permit bot to go
    sheet.update('F:F', curr_total.tolist())



def get_per_week(num_animals, num_redhearts):
    per_week = [] #array to hold each animal set's total output per week (assuming 3 posts week)
    for i in range(len(num_animals)):
        per_week.append(((num_animals[i]*2) + num_redhearts[i])*3)
    return per_week

async def increment_total(sheet):
    week_locs = sheet.col_values(5) #GETS PER WEEK COLUMN VALUES
    total_locs = sheet.col_values(6) # GET RUNNING TOTAL SO FAR
    newcol = []
    for i in range(1, len(week_locs)):
        # print(i, week_locs[i], total_locs[i])
        newcol.append([int(week_locs[i])+int(total_locs[i])])
    sheet.update('F2:F', newcol)
    # sheet.update_cells(newcol)
    await get_raccoon(sheet)

