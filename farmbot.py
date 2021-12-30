# bot.py
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext import tasks
import autofarmer
import botfuncs
import json
# import farmfunc

# BOT START AND LOOP
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='f!')
# channel = None

# client = discord.Client()

@tasks.loop(seconds=5)
async def check_for_rolling(channel):
    global isActive
    # print("STATE: ", botfuncs.getTrigger())
    # channel = bot.get_channel(603679783347421208) 
    # if channel:
    #     botfuncs.set_channel(channel)
    # else:
    #     print("Failed.", type(channel))

    # if botfuncs.getTrigger() == True:
        # You can put everything here, this is just an example
        # user = client.get_user(PUT_YOUR_USER_ID_HERE)
        # channel = bot.get_channel(603679783347421208) # flip-tests-bots-here channel
        # if channel:
            # botfuncs.set_channel(channel)
            # strings = await botfuncs.getContent()
            # for str in strings:
                # await channel.send(str)
            # await channel.send(botfuncs.getContent())
        # else:
        #     print("Failed.", type(channel))
        
        # await botfuncs.triggerTrue(False) # set it back to false
    # else:
        # pass


@bot.command()
async def register(ctx, *args):
    global bot
    #  await ctx.send('{} arguments: {}'.format(len(args), ', '.join(args)))
    await botfuncs.register_new(ctx, *args)


@bot.command()
async def roll(ctx, arg1):
    global bot
    arg1 = arg1.lower()
    if arg1  == 'off':
        await ctx.send(f"ok auto rolls off")
    elif arg1 == 'on':
        await ctx.send(f"ok on")
    elif arg1 == 'weekly':
        await ctx.send(f"aight bet lemme get ur stuff")
    else:
        await ctx.send(f"bitch idk what u sayin")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!!!!')
    channel = bot.get_channel(603679783347421208) # FLIP-TESTS-BOTS-HERE CHANNEL
    if channel:
        await botfuncs.set_channel(channel)
    else:
        print("Failed.", type(channel))
    check_for_rolling.start(channel)
    
    await botfuncs.set_bot(bot)
    await autofarmer.run_main() # UNCOMMENT LATER

bot.run(TOKEN)