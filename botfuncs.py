import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext import tasks


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