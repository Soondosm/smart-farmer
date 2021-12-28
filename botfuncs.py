import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext import tasks
import json
from apiclient import discovery

user_json = json.load(open('users.json'))
isActive = False
msg_content = None
channel = None
creds = None

async def set_creds(new_creds):
    creds = new_creds

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
    service = discovery.build('drive', 'v3', credentials=creds)
    stuff = service.files().list(
            pageSize=10, fields="files(name)").execute()
    items = stuff.get('files')
    sheet_names = []
    for n in items: sheet_names.append(n["name"])
    print(sheet_names)
    return sheet_names

async def register_new(ctx, *args):
    this_usr = ctx.message.author
    current_sheets = obtain_current_sheets()
    sheet_name = ' '.join(args)
    if this_usr in user_json["user_sheets"]:
        await ctx.send('{}, you have already registered your farm: {}.', this_usr.mention, user_json["user_sheets"][this_usr])
    if this_usr not in user_json["user_sheets"] and sheet_name in current_sheets: # if this user has no farm
        user_json["user_sheets"][this_usr] = sheet_name
    await ctx.send("{}, you added the spreadsheet named {}.".format(this_usr.mention, sheet_name))
    print()