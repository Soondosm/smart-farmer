# bot.py
import os

import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext import tasks
import autofarmer
import botfuncs
# import farmfunc

this_user = "bitch" # the person who is currently having their stuff rolled for



# BOT START AND LOOP
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='f.')

# client = discord.Client()

@tasks.loop(seconds=10)
async def check_for_rolling():
    global isActive
    if botfuncs.getTrigger() == True:
        # You can put everything here, this is just an example
        # user = client.get_user(PUT_YOUR_USER_ID_HERE)
        channel = bot.get_channel(603679783347421208) # flip-tests-bots-here channel
        if channel:
            await channel.send(botfuncs.getContent())
        else:
            print("Failed.", type(channel))
        
        await botfuncs.triggerTrue(False) # set it back to false
    else:
        pass




@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    check_for_rolling.start()
    await autofarmer.run_main()


bot.run(TOKEN)