import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

#Load variables from .env file
load_dotenv()

#Get token from .env file. Token is from the bot (see Discord develop)
TOKEN = os.getenv('DISCORD_TOKEN')

prefixCommand = "!"

#Create client, and remove built-in "help" command
client = commands.Bot(command_prefix=prefixCommand, help_command=None)

#Add Cogs/Extensions
client.load_extension("general")
client.load_extension("chessTournament")

#Event called when the discord bot is ready
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="chess_bot - !help"))
    print(f'{client.user} is connected and ready')

####################################################################################################
#                                                                                                  #
# WHEN CODE IN COGS NEEDS CHANGE, RELOAD IT. DECREASES DOWNTIME                                    #
#                                                                                                  #
####################################################################################################

#Command to reload an extension again, enables no downTime when editing new commands
@client.command()
async def reload(ctx, extension):
    await unload(ctx, extension)
    await load(ctx, extension)

#Command to upload an extension/cog
@client.command()
async def load(ctx, extension):
    client.load_extension(f"{extension}")
    print("Loaded " + extension)

#Command to unload an extension/cog
@client.command()
async def unload(ctx, extension):
    client.unload_extension(f"{extension}")
    print("Unloaded " + extension)


client.run(TOKEN)