import os

import discord
from discord.ext import commands

class Globals:

    def __init__(self):
        pass

    #Method initializes new embed
    def initializeEmbed(self, title=None, description=None, colour = discord.Colour.green()):

        newEmbed = discord.Embed(
            title = title,
            description = description,
            colour = colour
        )

        return newEmbed