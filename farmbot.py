# bot.py
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext import tasks
import autofarmer
import botfuncs
import json
from datetime import datetime
import aiocron

JSON_NAME = 'users.json'
# BOT START AND LOOP
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='f!')
bot.remove_command("help")
FIXED_CHANNEL = None # for reminders

# client = discord.Client()

# '* * * * *' every minute
@aiocron.crontab('0 9 * * 4') # every thursday at 9am
async def execute_reminder():
    print()
    print("Time met")
    global FIXED_CHANNEL
    global bot
    announce_string = "Greetings, Hellmouth Farmers! Today is Thursday EST, so this is your reminder to get your three weekly upkeep posts in before Sunday!\n"
    user_json = json.load(open(JSON_NAME))
    for usr, remind_val in user_json["user_remind"].items():
        if remind_val == "On":
            print(usr, remind_val)
            await bot.wait_until_ready()
            this_usr = await bot.fetch_user(int(usr))
            link = user_json["user_farmlinks"][str(usr)]
            announce_string+= f"{this_usr.mention}: {link} \n"

    await FIXED_CHANNEL.send(announce_string)

    

# @tasks.loop(seconds=10)
# async def check_for_reminder(channel):
#     print("Time met")
#     global FIXED_CHANNEL
#     global bot
#     announce_string = "Greetings, Hellmouth Farmers! Today is Thursday EST, so this is your reminder to get your three weekly upkeep posts in before Sunday!\n"
#     user_json = json.load(open(JSON_NAME))
#     for usr, remind_val in user_json["user_remind"].items():
#         if remind_val == "True":
#             print(usr, remind_val)
#             await bot.wait_until_ready()
#             this_usr = await bot.fetch_user(int(usr))
#             link = user_json["user_farmlinks"][str(usr)]
#             announce_string+= f"{this_usr.mention}: {link} \n"

#     await FIXED_CHANNEL.send(announce_string)


@bot.command()
async def help(ctx, *args):
    embed=discord.Embed(
        title="LINK TO SPREADSHEET TEMPLATE", 
        url="https://docs.google.com/spreadsheets/d/1TsedJaIPr19z-50NDVa79h4UDIJEZgGFkoHCmjg1GKo/edit#gid=0", 
        description="To get started: \n**1.** Follow the link above to the spreadsheet template." +
"\n**2.** Go to File -> Make a Copy." + 
"\n**3.** Name your new spreadsheet something unique. "+
"\n**4.** Share this spreadsheet and give *EDITING PRIVILEGES* to the following email address:"+ 
"`autofarming@autofarming.iam.gserviceaccount.com` "+
"\n**5.** Type f!register [YOUR SPREADSHEETNAME]. "+
"Have your farm's HELLMOUTH URL ready, because you will be asked to provide it.\n"+
"\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\n"+
"\nThen you are good to go! You DO NOT need to edit any values in your spreadsheet "+ 
"because the script will fetch the number of animals for you. "+ 
"If you already started with materials, you may edit them into the totals column.\n", color=0x3eb300)
    embed.add_field(name="f!register (my spreadsheet name)", value="register a new farm. Your spreassheet name is case sensitive. Have your farm's URL ready, as you will be asked to enter it to complete registration. If everything was done correctly, you should see your spreadsheet populate with your farm's data.", inline=False)
    embed.add_field(name="f!show", value="get the animals currently in your farm, as well as their weekly produce.", inline=False)
    embed.add_field(name="f!edit [farm OR sheet]", value="change either your farm link or the name of your spreadsheet, respectively.", inline=False)
    embed.add_field(name="f!sync", value="If you bought an animal in the middle of the week and want to see what it will give you on Sunday, use this command to sync your farm post with your spreadsheet.", inline=False)
    embed.add_field(name="f!roll [tools OR weekly]", value="tools: roll fishing rods and bug nets to collect the rewards they provide upon finishing threads in places appropriate for them. \n weekly: your weekly farm roll. Execute this command to roll crops, randomized animals, nets and rods, and increment all animal producers. Then add all of these yields to your spreadsheet and report new total.", inline=False)
    embed.add_field(name="f!remind [on OR off]", value="Toggle whether I ping you a reminder on Thursdays at 9am EST to make your farm upkeep posts.", inline=False)

    embed.set_footer(text="Questions? Encountering bugs? Ping or dm Flip in the server!")
    await ctx.send(embed=embed)

@bot.command()
async def register(ctx, *args):
    global bot
    #  await ctx.send('{} arguments: {}'.format(len(args), ', '.join(args)))
    await botfuncs.register_new(ctx, *args)

@bot.command()
async def remind(ctx, *args):
    global bot
    await botfuncs.remind_me(ctx, *args)

@bot.command()
async def roll(ctx, *args):
    global bot
    await botfuncs.roll_items(ctx, *args)

@bot.command()
async def edit(ctx, *args):
    await botfuncs.edit_info(ctx, *args)

@bot.command()
async def show(ctx, *args):
    await botfuncs.show_farm(ctx, *args)

@bot.command()
async def sync(ctx, *args):
    await botfuncs.sync_sheet(ctx, *args)

@bot.event
async def on_ready():
    global FIXED_CHANNEL
    print(f'{bot.user} has connected to Discord!!!!')
    FIXED_CHANNEL = bot.get_channel(603679783347421208) # FLIP-TESTS-BOTS-HERE CHANNEL
    if FIXED_CHANNEL:
        await botfuncs.set_channel(FIXED_CHANNEL)
    else:
        print("Failed.", type(FIXED_CHANNEL))
    # check_for_reminder.start(FIXED_CHANNEL)
    
    await botfuncs.set_bot(bot) # set the botfuncs.py bot to this bot so we can keep track
    await botfuncs.initialize_client() # boot up google spreadsheet client
    # await autofarmer.run_main('TEST1') # UNCOMMENT LATER

bot.run(TOKEN)