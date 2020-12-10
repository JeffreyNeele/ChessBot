import reactionEmojis as reactEmoji
import math
import globalFunctions

import discord
from discord.ext import commands

whitespace = "\u200b"

#Class defines general bot commands
class General(commands.Cog):

    emojiHandler = reactEmoji.ReactionEmojis()
    globalHandler = globalFunctions.Globals()


    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("General Cog is ready")

    @commands.command()
    # help: Command which gives an explanation for what each command does
    async def help(self, ctx):

        try:
            if ctx.message.author.guild_permissions.administrator:
                embedList, page, maxPage = self.createAdministratorHelp()
            else:
                embedList, page, maxPage = self.createGeneralHelp()
        except:
            embedList, page, maxPage = self.createGeneralHelp()

        embedHelp = embedList[page]
        sendEmbed = await ctx.send(embed=embedHelp)

        #Add necessary reactions to the embed
        await self.emojiHandler.addEmojis(self.emojiHandler.getPageEmojis(), sendEmbed)

        #Check function: 
        def checkResponse(reaction, user):
            return reaction.emoji in self.emojiHandler.getPageEmojis() and reaction.message.id == sendEmbed.id

        #React to emote interaction when necessary
        while True:
            try:
                reaction, user = await self.client.wait_for("reaction_add", check=checkResponse, timeout=None)
            except:
                print("no response")
                break
            else:
                
                newPage = self.emojiHandler.processPageEmoji(reaction.emoji, page, maxPage)
                if page != newPage:
                    page = newPage
                    embedHelp = embedList[page]

                    #Edit embed message
                    await sendEmbed.edit(embed=embedHelp)
                
                #Delete emoji, but only when not in DM Channel (because DM channel does not allow that)
                if ctx.message.channel.type != discord.ChannelType.private:
                    await sendEmbed.remove_reaction(reaction.emoji, ctx.message.author)
    
    # announce: Command which announces a message to the announcement of the "Black Sprites" server
    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def announce(self, ctx, *, message):

        channel = discord.utils.get(ctx.guild.text_channels, name="announcements")
        try:
            attachment = await ctx.message.attachments[0].to_file()
            await channel.send(message, file=attachment)
        except: #The announcement does not contain an image
            await channel.send(message)
    
    ####################################################################################################
    #                                                                                                  #
    # ASSISTING METHODS                                                                                #
    #                                                                                                  #
    ####################################################################################################

    #Help - seen bij users with administrator permission
    def createAdministratorHelp(self):

        prefixCommands = self.client.command_prefix
        embedList = []
        startPage = self.globalHandler.initializeEmbed(title="Welcome to the help guide", description="Here you will find table of content for the command pages")
        embedList.append(startPage)
        count = 1

        #FIRST PAGE - GENERAL COMMANDS
        firstPageCommands = {
            "announce A" : "Make announcements to a channel named announcement in the server.\nA = message. Also able to attach an image to the message!"
        }

        firstPage = self.globalHandler.initializeEmbed(title="General commands", description="Commands useful anytime")
        for command in list(firstPageCommands.keys()):
            firstPage.add_field(name=f"{count}" + ": " + prefixCommands + command, value=firstPageCommands[command], inline=False)
            count += 1
        embedList.append(firstPage)

        #SECOND PAGE - BEFORE CREATING A TOURNAMENT
        secondPageCommands = {
            "signup A" : "Sign up a player for the tournament, A = player to be signed up.",
            "signout A" : "Sign out a player from the tournament, A = player to be signed out.",
            "players" : "Show all players currently signed up.",
            "reset" : "Deletes all current users and groups."
        }

        secondPage = self.globalHandler.initializeEmbed(title="Before creating a tournament", description="Commands useful before creating a tournament")
        for command in list(secondPageCommands.keys()):
            secondPage.add_field(name=f"{count}" + ": " + prefixCommands + command, value=secondPageCommands[command], inline=False)
            count += 1
        embedList.append(secondPage)

        #THIRD PAGE - DURING THE TOURNAMENT
        thirdPageCommands = {
            "createtourney A" : "Create a tournament with current players, A = amount of groups in competition.",
            "changestats" : "Change the stats from players in the tournament.",
            "groups" : "Show all groups of the current tournament."
        }

        thirdPage = self.globalHandler.initializeEmbed(title="During a tournament", description="Commands useful during a tournament")
        for command in list(thirdPageCommands.keys()):
            thirdPage.add_field(name=f"{count}" + ": " + prefixCommands + command, value=thirdPageCommands[command], inline=False)
            count += 1
        
        embedList.append(thirdPage)

        #Fill startpage content
        valuePages = "Page 1:"
        valueContentOfPage = embedList[1].title
        for i in range(2, len(embedList), 1):
            valuePages += "\nPage " + str(i) + ":"
            valueContentOfPage += "\n" + embedList[i].title 

        embedList[0].add_field(name="Content", value=valuePages, inline=True)
        embedList[0].add_field(name=whitespace, value=valueContentOfPage, inline=True)

        #SET FOOTER OF EMBEDS
        page = 0
        maxPage = len(embedList) - 1
        for i in range(0, len(embedList), 1):
            embedList[i].set_footer(text="page: " + str(i) + " of " + str(maxPage))
        
        return embedList, page, maxPage

    #Help - only seen by non-administrator users
    def createGeneralHelp(self):
        prefixCommands = self.client.command_prefix
        embedList = []
        count = 1

        firstPageCommands = {
            "groups" : "Show all groups of the current tournament."
        }

        firstPage = self.globalHandler.initializeEmbed(title="Help", description="Here you will find commands usable by everyone")
        for command in list(firstPageCommands.keys()):
            firstPage.add_field(name=f"{count}" + ": " + prefixCommands + command, value=firstPageCommands[command], inline=False)
            count += 1
        
        embedList.append(firstPage)

        #SET FOOTER OF EMBEDS
        page = 0
        maxPage = len(embedList) - 1
        for i in range(0, len(embedList), 1):
            embedList[i].set_footer(text="page: " + str(i + 1) + " of " + str(maxPage + 1))
        
        return embedList, page, maxPage

def setup(client):
    client.add_cog(General(client))