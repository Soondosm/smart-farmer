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


async def register_new(ctx, *args):
    this_usr = ctx.message.author
    if this_usr not in user_json["user_sheets"]: # if this user has no farm
        user_json["user_sheets"][this_usr] = ""
    await ctx.send("{} is your id".format(this_usr.mention))
    print()