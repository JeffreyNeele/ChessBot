import os
import json
import random
import math

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

#Variables for file paths
usersFile = "users.json"
groupsFile = "groups.json"

#Variables for users.json indexing
userList = "users"
groupsList = "groups"

#The reaction emotes
#Get emote in discord by typing \(insert emote here)
#Emotes to go through pages
firstPageEmote = "⏪"
lastPageEmote = "◀️"
nextPageEmote = "▶️"
endPageEmote = "⏩"
emojisPages = [firstPageEmote, lastPageEmote, nextPageEmote, endPageEmote]

#Emotes for yes/no answers
yesEmote = "🇾"
noEmote = "🇳"
emojisAnswers = [yesEmote, noEmote]

#Emotes to go through 1-10 options
oneEmote = "1️⃣"
twoEmote = "2️⃣"
threeEmote = "3️⃣"
fourEmote = "4️⃣"
fiveEmote = "5️⃣"
sixEmote = "6️⃣"
sevenEmote = "7️⃣"
eightEmote = "8️⃣"
nineEmote = "9️⃣"
tenEmote = "🔟"
emojiNumbers = [oneEmote, twoEmote, threeEmote, fourEmote, fiveEmote, sixEmote, sevenEmote, eightEmote, nineEmote, tenEmote]

#Emotes to give wins/draws/loses to players
winUp = "✅"
winDown = "❎"
drawUp = "⬜"
drawDown = "🔳"
loseUp = "❤️"
loseDown = "💔"
emojiWinDrawLose = [winUp, winDown, drawUp, drawDown, loseUp, loseDown]


#Event called when the discord bot is ready
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="chess_bot - !help"))
    
    #Create necessary files (if they are not present)
    #File with users
    try:
        file = open(usersFile, "r")
    except:
        file = open(usersFile, "w")
        usersInfo = {}
        usersInfo[userList] = {}
        json.dump(usersInfo, file)
    finally:
        file.close()
    
    #File with poules
    try:
        file = open(groupsFile, "r")
    except:
        file = open(groupsFile, "w")
        groupsInfo = {}
        groupsInfo[groupsList] = {}
        json.dump(groupsInfo, file)
    finally:
        file.close()
    
    print(f'{client.user} is connected and ready')

@client.event
async def on_message(message):

    #Return when author is the bot - prevents infinite recursion
    if message.author == client.user:
        return
    else:
        await client.process_commands(message)

####################################################################################################
#                                                                                                  #
# COMMANDS                                                                                         #
#                                                                                                  #
####################################################################################################

# help: Command which gives an explanation for what each command does
@client.command()
async def help(ctx):

    #Dictionary - Key = command call, Value = explanation of command
    commandDict = {
        "changestats" : "Change the stats from players in the tournament",
        "createtourney A" : "Create a tournament with current players, A = amount of groups in competition",
        "groups" : "Show all groups of the current tournament",
        "players" : "Show all players currently signed up",
        "reset" : "Deletes all current users and groups",
        "signup A" : "Sign up a player for the tournament, A = player to be signed up",
        "signout A" : "Sign out a player from the tournament, A = player to be signed out"
    }

    commandDictKeys = list(commandDict.keys())

    page = 0
    shownCommands = 4
    maxPage = math.floor(len(commandDict) / shownCommands)

    #Initialize embed, which makes a nice looking window
    embedHelp = initializeEmbed(title="Help - Chess bot", description="A guide to all the commands")
    embedHelp.set_footer(text="page: " + str(page + 1) + " of " + str(maxPage + 1))

    lowCommand = page * shownCommands
    maxCommand = lowCommand + shownCommands

    #Add first page to the embed
    #If not at max page
    if maxCommand < len(commandDictKeys):
        maxRange = maxCommand
    else:
        maxRange = len(commandDictKeys)

    for i in range(lowCommand, maxRange, 1):
        nameField = f'{i + 1}' + ': ' + prefixCommand + commandDictKeys[i]
        valueField = commandDict[commandDictKeys[i]]
        embedHelp.add_field(name=nameField, value=valueField, inline=False)

    sendEmbed = await ctx.send(embed=embedHelp)

    #Add necessary reactions to the embed
    await addEmotes(emojisPages, sendEmbed)

    #Check function: 
    def checkResponse(reaction, user):
        return reaction.emoji in emojisPages and reaction.message.id == sendEmbed.id and user == ctx.message.author

    #React to emote interaction when necessary
    while True:
        try:
            reaction, user = await client.wait_for("reaction_add", check=checkResponse, timeout=None)
        except:
            print("no response")
        else:

            if reaction.emoji == firstPageEmote:
                page = 0
            elif reaction.emoji == lastPageEmote:
                if page > 0:
                    page -= 1
            elif reaction.emoji == nextPageEmote:
                if page < maxPage:
                    page += 1
            else:
                page = maxPage
            
            embedHelp.clear_fields()
            embedHelp.set_footer(text="page: " + str(page + 1) + " of " + str(maxPage + 1))

            lowCommand = page * shownCommands
            maxCommand = lowCommand + shownCommands

            #If not at max page
            if maxCommand < len(commandDictKeys):
                maxRange = maxCommand
            else:
                maxRange = len(commandDictKeys)

            for i in range(lowCommand, maxRange, 1):
                nameField = f'{i + 1}' + ': ' + prefixCommand + commandDictKeys[i]
                valueField = commandDict[commandDictKeys[i]]
                embedHelp.add_field(name=nameField, value=valueField, inline=False)

            #Edit embed message
            await sendEmbed.edit(embed=embedHelp)
            await sendEmbed.remove_reaction(reaction.emoji, ctx.author)

# changestats: Command enables user to change the stats from players in the tournament
@client.command()
async def changestats(ctx):

    groupsInfo = readFileInfo(groupsFile)
    allGroups = groupsInfo[groupsList]
    allPlayers = {}

    for groups in allGroups:
        for i in range(0, len(allGroups[groups]["players"]), 1):
            namePlayer = allGroups[groups]["players"][i]["name"]
            wins = allGroups[groups]["players"][i]["wins"]
            draws = allGroups[groups]["players"][i]["draws"]
            loses = allGroups[groups]["players"][i]["loses"]

            allPlayers[namePlayer] = {"group" : groups, "wins" : wins, "draws" : draws, "loses" : loses}

    playerListKeys = list(allPlayers)

    page = 0
    shownPlayers = 10
    maxPage = math.floor(len(allPlayers) / shownPlayers)

    #Initialize embed to show all the players
    embedPlayerslist = initializeEmbed(title="Player list", description="Choose the player you want to change the stats for\nusing emoticons 1 through 10")
    embedPlayerslist.set_footer(text="page: " + str(page + 1) + " of " + str(maxPage + 1))

    lowPlayer = page * shownPlayers
    maxPlayer = lowPlayer + shownPlayers

    nameFieldPlayers = "Players"
    valueFieldPlayers = ""
    nameFieldGroups = "In group"
    valueFieldGroups = ""
    nameFieldWinDrawLose = "Win/Draw/Lose"
    valueFieldWinDrawLose = ""

    #Add first page to the embed
    #If not at max page
    if maxPlayer < len(playerListKeys):
        for i in range(lowPlayer, maxPlayer, 1):
            valueFieldPlayers += f"{i + 1}" + ": " + playerListKeys[i] + "\n"
            valueFieldGroups += allPlayers[playerListKeys[i]]["group"] + "\n"
            valueFieldWinDrawLose += str(allPlayers[playerListKeys[i]]["wins"]) + " - " + str(allPlayers[playerListKeys[i]]["draws"]) + " - " + str(allPlayers[playerListKeys[i]]["loses"]) + "\n"
    else: #At max page
        for i in range(lowPlayer, len(playerListKeys), 1):
            valueFieldPlayers += f"{i + 1}" + ": " + playerListKeys[i] + "\n"
            valueFieldGroups += allPlayers[playerListKeys[i]]["group"] + "\n"
            valueFieldWinDrawLose += str(allPlayers[playerListKeys[i]]["wins"]) + " - " + str(allPlayers[playerListKeys[i]]["draws"]) + " - " + str(allPlayers[playerListKeys[i]]["loses"]) + "\n"

    embedPlayerslist.add_field(name=nameFieldPlayers, value=valueFieldPlayers, inline=True)
    embedPlayerslist.add_field(name=nameFieldGroups, value=valueFieldGroups, inline=True)
    embedPlayerslist.add_field(name=nameFieldWinDrawLose, value=valueFieldWinDrawLose, inline=True)

    #Initialize embed to show the player stats
    embedPlayerChange = initializeEmbed(title="No player selected", description="please choose a player in the previous section")
    embedPlayerChange.set_footer(text="add/delete Win: " + winUp + "/" + winDown + " | add/delete Draw: " + drawUp + "/" + drawDown + " | add/delete Lose: " + loseUp + "/" + loseDown)

    playerListEmbed = await ctx.send(embed=embedPlayerslist)
    playerEmbed = await ctx.send(embed=embedPlayerChange)

    #Add emotes
    await addEmotes(emojisPages, playerListEmbed)
    await addEmotes(emojiNumbers, playerListEmbed)
    await addEmotes(emojiWinDrawLose, playerEmbed)

    def checkReaction(reaction, user):
        if user != ctx.message.author:
            return False
        elif reaction.message.id == playerListEmbed.id and (reaction.emoji in emojisPages or reaction.emoji in emojiNumbers):
            return True
        elif reaction.message.id == playerEmbed.id and reaction.emoji in emojiWinDrawLose:
            return True
        else:
            return False

    while True:

        try:
            reaction, user = await client.wait_for("reaction_add", check=checkReaction, timeout=None)
        except:
            await ctx.send("Oops, something went wrong, please try again!")
            break
        else:

            #User wants to change pages
            if reaction.emoji in emojisPages:
                
                #Change page nr
                if reaction.emoji == firstPageEmote:
                    page = 0
                elif reaction.emoji == lastPageEmote:
                    if page > 0:
                        page -= 1
                elif reaction.emoji == nextPageEmote:
                    if page < maxPage:
                        page += 1
                else:
                    page = maxPage

                #Rebuild fields
                embedPlayerslist.clear_fields()

                lowPlayer = page * shownPlayers
                maxPlayer = lowPlayer + shownPlayers

                valueFieldPlayers = ""
                valueFieldGroups = ""
                valueFieldWinDrawLose = ""

                #Add new page to the embed
                #If not at max page
                if maxPlayer < len(playerListKeys):
                    for i in range(lowPlayer, maxPlayer, 1):
                        valueFieldPlayers += f"{i + 1}" + ": " + playerListKeys[i] + "\n"
                        valueFieldGroups += allPlayers[playerListKeys[i]]["group"] + "\n"
                        valueFieldWinDrawLose += str(allPlayers[playerListKeys[i]]["wins"]) + " - " + str(allPlayers[playerListKeys[i]]["draws"]) + " - " + str(allPlayers[playerListKeys[i]]["loses"]) + "\n"
                else: #At max page
                    for i in range(lowPlayer, len(playerListKeys), 1):
                        valueFieldPlayers += f"{i + 1}" + ": " + playerListKeys[i] + "\n"
                        valueFieldGroups += allPlayers[playerListKeys[i]]["group"] + "\n"
                        valueFieldWinDrawLose += str(allPlayers[playerListKeys[i]]["wins"]) + " - " + str(allPlayers[playerListKeys[i]]["draws"]) + " - " + str(allPlayers[playerListKeys[i]]["loses"]) + "\n"

                embedPlayerslist.add_field(name=nameFieldPlayers, value=valueFieldPlayers, inline=True)
                embedPlayerslist.add_field(name=nameFieldGroups, value=valueFieldGroups, inline=True)
                embedPlayerslist.add_field(name=nameFieldWinDrawLose, value=valueFieldWinDrawLose, inline=True)

                #Edit fields and remove reaction
                await playerListEmbed.edit(embed=embedPlayerslist)
                await playerListEmbed.remove_reaction(reaction.emoji, ctx.author)
            #User picked a player
            elif reaction.emoji in emojiNumbers:
                
                indexEmoji = emojiNumbers.index(reaction.emoji)

                if indexEmoji + lowPlayer >= len(playerListKeys):
                    await playerListEmbed.remove_reaction(reaction.emoji, ctx.author)
                    continue

                selectedPlayer = playerListKeys[lowPlayer + indexEmoji]
                
                #Change some properties of the embed before giving new information
                embedPlayerChange.title = selectedPlayer
                embedPlayerChange.description = "What would you like to do for " + selectedPlayer + "?"
                embedPlayerChange.clear_fields()

                #Wins
                embedPlayerChange.add_field(name="Wins:", value=allPlayers[selectedPlayer]["wins"])
                #Draws
                embedPlayerChange.add_field(name="Draws:", value=allPlayers[selectedPlayer]["draws"])
                #Loses
                embedPlayerChange.add_field(name="Loses:", value=allPlayers[selectedPlayer]["loses"])

                await playerEmbed.edit(embed=embedPlayerChange)
                await playerListEmbed.remove_reaction(reaction.emoji, ctx.author)
            #User changed stats from player
            else:   #reaction.emoji in emojiWinDrawLose

                if selectedPlayer != "":

                    if reaction.emoji == winUp:
                        allPlayers[selectedPlayer]["wins"] += 1
                    elif reaction.emoji == winDown and allPlayers[selectedPlayer]["wins"] > 0:
                        allPlayers[selectedPlayer]["wins"] -= 1
                    elif reaction.emoji == drawUp:
                        allPlayers[selectedPlayer]["draws"] += 1
                    elif reaction.emoji == drawDown and allPlayers[selectedPlayer]["draws"] > 0:
                        allPlayers[selectedPlayer]["draws"] -= 1
                    elif reaction.emoji == loseUp:
                        allPlayers[selectedPlayer]["loses"] += 1
                    elif reaction.emoji == loseDown and allPlayers[selectedPlayer]["loses"] > 0:
                        allPlayers[selectedPlayer]["loses"] -= 1

                    #Rebuild playerList
                    embedPlayerslist.clear_fields()

                    valueFieldPlayers = ""
                    valueFieldGroups = ""
                    valueFieldWinDrawLose = ""

                    #Add new page to the embed
                    #If not at max page
                    if maxPlayer < len(playerListKeys):
                        for i in range(lowPlayer, maxPlayer, 1):
                            valueFieldPlayers += f"{i + 1}" + ": " + playerListKeys[i] + "\n"
                            valueFieldGroups += allPlayers[playerListKeys[i]]["group"] + "\n"
                            valueFieldWinDrawLose += str(allPlayers[playerListKeys[i]]["wins"]) + " - " + str(allPlayers[playerListKeys[i]]["draws"]) + " - " + str(allPlayers[playerListKeys[i]]["loses"]) + "\n"
                    else: #At max page
                        for i in range(lowPlayer, len(playerListKeys), 1):
                            valueFieldPlayers += f"{i + 1}" + ": " + playerListKeys[i] + "\n"
                            valueFieldGroups += allPlayers[playerListKeys[i]]["group"] + "\n"
                            valueFieldWinDrawLose += str(allPlayers[playerListKeys[i]]["wins"]) + " - " + str(allPlayers[playerListKeys[i]]["draws"]) + " - " + str(allPlayers[playerListKeys[i]]["loses"]) + "\n"

                    embedPlayerslist.add_field(name=nameFieldPlayers, value=valueFieldPlayers, inline=True)
                    embedPlayerslist.add_field(name=nameFieldGroups, value=valueFieldGroups, inline=True)
                    embedPlayerslist.add_field(name=nameFieldWinDrawLose, value=valueFieldWinDrawLose, inline=True)

                    #Rebuild playerField

                    embedPlayerChange.clear_fields()
                    #Wins
                    embedPlayerChange.add_field(name="Wins:", value=allPlayers[selectedPlayer]["wins"])
                    #Draws
                    embedPlayerChange.add_field(name="Draws:", value=allPlayers[selectedPlayer]["draws"])
                    #Loses
                    embedPlayerChange.add_field(name="Loses:", value=allPlayers[selectedPlayer]["loses"])

                    await playerListEmbed.edit(embed=embedPlayerslist)
                    await playerEmbed.edit(embed=embedPlayerChange)
                await playerEmbed.remove_reaction(reaction.emoji, ctx.author)

# createtourney: Command creates new competition
@client.command()
async def createtourney(ctx, groupAmount):

    groupsInfo = readFileInfo(groupsFile)

    #Check if a current tournament is setup
    if bool(groupsInfo[groupsList]):

        #Check if the user is confident in creating a new tourney, thus overiding the old tournament information
        confidenceCheckMessage = await ctx.send("There already is a current competition.\nAre you sure you want to create a new one?")

        #Add emojis
        await addEmotes(emojisAnswers, confidenceCheckMessage)

        def checkConfidence(reaction, user):
            return reaction.emoji in emojisAnswers and reaction.message.id == confidenceCheckMessage.id and user == ctx.message.author

        #Wait for user reaction. Only break the while loop if the user reacted with yes
        while True:
            try:
                reaction, user = await client.wait_for("reaction_add", check=checkConfidence, timeout=20)
            except:
                await confidenceCheckMessage.edit(content="Sorry, you are timed out. Please try again!")
                return
            else:

                if reaction.emoji == yesEmote:
                    break
                else:
                    await confidenceCheckMessage.edit(content="Ok, I will not create a new tournament")
                    return
                

    #Get players
    usersInfo = readFileInfo(usersFile)
    allUsers = usersInfo[userList]

    #Create variables for groups.json
    groupsInfo = {}
    groupsInfo[groupsList] = {}
    
    #Create the groups
    groupAmount = int(groupAmount)

    for nr in range(1, groupAmount + 1, 1):
        groupName = "Group " + str(nr)
        groupsInfo[groupsList] = createGroup(groupName, groupsInfo[groupsList])

    listOfKeys = list(allUsers.keys())

    #Fill the groups
    while bool(allUsers):

        #Fill the groups in order, but choose the player randomly
        #iterating in order allows for equal distribution of players
        for nr in range(1, groupAmount + 1, 1):
            if not bool(allUsers): #No players left to add
                break
            else:
                playerChoice = random.choice(listOfKeys)
                listOfKeys.remove(playerChoice)
                player = allUsers.pop(playerChoice)

                groupName = "Group " + str(nr)
                groupsInfo[groupsList][groupName]["players"].append(player)
    
    writeFileInfo(groupsFile, groupsInfo)

    try:
        await confidenceCheckMessage.edit(content="Tournament is all set up")
    except:
        await ctx.send("Tournament is all set up")
    finally:
        await groups(ctx)

# groups: Command shows all the groups
@client.command()
async def groups(ctx):
    
    with open(groupsFile, "r") as file:
        groupsInfo = json.load(file)
        file.close()
    
    #Check if there are groups available
    if not bool(groupsInfo[groupsList]):
        await ctx.send("At the moment there are no groups available to show")
        return
    
    groupListKeys = list(groupsInfo[groupsList].keys())

    page = 0
    maxPage = len(groupListKeys) - 1

    #Initialize embed, which makes a nice looking window
    embedGroups = initializeEmbed(title=groupListKeys[page], description="All players in " + groupListKeys[page])
    embedGroups.set_footer(text="page: " + str(page + 1) + " of " + str(maxPage + 1))

    nameFieldPlayers = "Players"
    valueFieldPlayers = ""

    nameFieldWinDrawLose = "Win/Draw/Lose"
    valueFieldWinDrawLose = ""

    #Add first page to the embed
    playersInGroup = groupsInfo[groupsList][groupListKeys[page]]["players"]

    for i in range(0, len(playersInGroup), 1):
        #Add playerlist
        valueFieldPlayers += f"{i + 1}" + ": " + playersInGroup[i]["name"] + "\n"

        #Add win/draws/loses
        valueFieldWinDrawLose += str(playersInGroup[i]["wins"]) + " - " + str(playersInGroup[i]["draws"]) + " - " + str(playersInGroup[i]["loses"]) + "\n"
    
    embedGroups.add_field(name=nameFieldPlayers, value=valueFieldPlayers, inline=True)
    embedGroups.add_field(name=nameFieldWinDrawLose, value=valueFieldWinDrawLose, inline=True)
    sendEmbed = await ctx.send(embed=embedGroups)

    #Add necessary reactions to the embed
    await addEmotes(emojisPages, sendEmbed)

    #Check function: 
    def checkResponse(reaction, user):
        return reaction.emoji in emojisPages and reaction.message.id == sendEmbed.id and user == ctx.message.author

    #React to emote interaction when necessary
    while True:
        try:
            reaction, user = await client.wait_for("reaction_add", check=checkResponse, timeout=None)
        except:
            print("no response")
        else:

            if reaction.emoji == firstPageEmote:
                page = 0
            elif reaction.emoji == lastPageEmote:
                if page > 0:
                    page -= 1
            elif reaction.emoji == nextPageEmote:
                if page < maxPage:
                    page += 1
            else:
                page = maxPage

            #Initialize embed, which makes a nice looking window
            embedGroups.title = groupListKeys[page]
            embedGroups.description = "All players in " + groupListKeys[page]
            embedGroups.set_footer(text="page: " + str(page + 1) + " of " + str(maxPage + 1))

            embedGroups.clear_fields()
            valueFieldPlayers = ""
            valueFieldWinDrawLose = ""

            #Add first page to the embed
            playersInGroup = groupsInfo[groupsList][groupListKeys[page]]["players"]

            for i in range(0, len(playersInGroup), 1):
                #Add playerlist
                valueFieldPlayers += f"{i + 1}" + ": " + playersInGroup[i]["name"] + "\n"

                #Add win/draws/loses
                valueFieldWinDrawLose += str(playersInGroup[i]["wins"]) + " - " + str(playersInGroup[i]["draws"]) + " - " + str(playersInGroup[i]["loses"]) + "\n"
            
            embedGroups.add_field(name=nameFieldPlayers, value=valueFieldPlayers, inline=True)
            embedGroups.add_field(name=nameFieldWinDrawLose, value=valueFieldWinDrawLose, inline=True)

            #Edit embed message
            await sendEmbed.edit(embed=embedGroups)
            await sendEmbed.remove_reaction(reaction.emoji, ctx.author)

# allPlayers: Command shows all players in users.json (all signed up players)
@client.command()
async def players(ctx):

    #Get players
    usersInfo = readFileInfo(usersFile)

    if not bool(usersInfo[userList]):
        await ctx.send("No players available to show")
        return
    
    #Variables to create embed fields
    userKeys = list(usersInfo[userList].keys())
    page = 0
    shownPlayers = 10
    maxPage = math.floor(len(userKeys) / shownPlayers)
    lowAmount = page * shownPlayers
    maxAmount = lowAmount + shownPlayers

    #Initialize embed, which makes a nice looking window
    embedHelp = discord.Embed(
        title = 'Player list',
        description = 'List of all players',
        colour = discord.Colour.green()
    )
    embedHelp.set_footer(text="page: " + str(page + 1) + " of " + str(maxPage + 1))

    #Create embed field
    nameField = "Players"
    valueField = ""

    #Check if current page is not max page
    if maxAmount < len(userKeys):
        for i in range(lowAmount, maxAmount, 1):
            valueField += f'{i + 1}' + ": " + usersInfo[userList][userKeys[i]]["name"] + "\n"
    else: #max page
        for i in range(lowAmount, len(userKeys), 1):
            valueField += f'{i + 1}' + ": " + usersInfo[userList][userKeys[i]]["name"] + "\n"
    embedHelp.add_field(name=nameField, value=valueField, inline=False)

    sendEmbed = await ctx.send(embed=embedHelp)

    #Add necessary reactions to the embed
    await addEmotes(emojisPages, sendEmbed)
    # for emote in emojisPages:
    #     await sendEmbed.add_reaction(emote)

    #Check function: 
    def checkResponse(reaction, user):
        if reaction.emoji in emojisPages and reaction.message.id == sendEmbed.id and user == ctx.message.author:
            return True
        else:
            return False

    #React to emote interaction when necessary
    while True:
        try:
            reaction, user = await client.wait_for("reaction_add", check=checkResponse, timeout=None)
        except:
            print("no response")
            break
        else:

            if reaction.emoji == firstPageEmote:
                page = 0
            elif reaction.emoji == lastPageEmote:
                if page > 0:
                    page -= 1
            elif reaction.emoji == nextPageEmote:
                if page < maxPage:
                    page += 1
            else:
                page = maxPage

            embedHelp = discord.Embed(
                title = 'Player list',
                description = 'List of all players',
                colour = discord.Colour.green()
            )

            embedHelp.set_footer(text="page: " + str(page + 1) + " of " + str(maxPage + 1))
            
            lowAmount = page * shownPlayers
            maxAmount = lowAmount + shownPlayers

            nameField = "Players"
            valueField = ""

            #Check if current page is not max page
            if maxAmount < len(userKeys):
                for i in range(lowAmount, maxAmount, 1):
                    valueField += f'{i + 1}' + ": " + usersInfo[userList][userKeys[i]]["name"] + "\n"
            else: #max page
                for i in range(lowAmount, len(userKeys), 1):
                    valueField += f'{i + 1}' + ": " + usersInfo[userList][userKeys[i]]["name"] + "\n"
            embedHelp.add_field(name=nameField, value=valueField, inline=False)

            #Edit embed message
            await sendEmbed.edit(embed=embedHelp)
            await sendEmbed.remove_reaction(reaction.emoji, ctx.author)

# reset: deletes all users from users.json and all groups from groups.json
#TODO: Enable Yes/No emote interaction
@client.command()
async def reset(ctx):

    #Ask if the user is confident in deleting all the information
    confidenceCheckMessage = await ctx.send("Are you sure you want to delete all users and groups?")
    await addEmotes(emojisAnswers, confidenceCheckMessage)

    #Check function - original author can only answer
    def checkConfidence(reaction, user):
            return reaction.emoji in emojisAnswers and reaction.message.id == confidenceCheckMessage.id and user == ctx.message.author

    try:
        reaction, user = await client.wait_for("reaction_add", check=checkConfidence, timeout=20)
    except:
        await ctx.send("Timed out. Please try again.")
    else:   
        if reaction.emoji == yesEmote:
            #users.json
            usersInfo = {}
            usersInfo[userList] = {}
            writeFileInfo(usersFile, usersInfo)

            #groups.json
            groupsInfo = {}
            groupsInfo[groupsList] = {}
            writeFileInfo(groupsFile, groupsInfo)

            await confidenceCheckMessage.edit(content="Ok, I deleted all users and groups!")
        else:
            await confidenceCheckMessage.edit(content="Ok, I will leave it then.")

# signup: Command lets a user sign up for the competition
@client.command()
async def signup(ctx, *, target):

    #Get current player list
    usersInfo = readFileInfo(usersFile)
    
    #Add new player to the list
    usersInfo = createUser(ctx, target, usersInfo)

    if usersInfo is None:
        await ctx.send(target + " is already signed up")
    else:
        #Update users.json
        writeFileInfo(usersFile, usersInfo)

        await ctx.send(target + " is signed in!")

# signout: Command lets a user sign out of the competition
@client.command()
async def signout(ctx, *, target):

    usersInfo = readFileInfo(usersFile)
    
    if target in usersInfo[userList]:
        del usersInfo[userList][target]
        await ctx.send(target + " is removed from the players list")
    else:
        await ctx.send(target + " is not an existant player")
    
    writeFileInfo(usersFile, usersInfo)

####################################################################################################
#                                                                                                  #
# ASSISTING METHODS                                                                                #
#                                                                                                  #
####################################################################################################

#Method for adding standard emotes to messages
async def addEmotes(emoteList, message):

    for emote in emoteList:
        await message.add_reaction(emote)

#Method calculates the placements of each member in the groups - uses mergesort
def calculateGroupPlacements(playersInGroup):  
    return mergeSortPlayers(playersInGroup, 0, len(playersInGroup) - 1)

#Method returns the player who is greater/superior/higher/...
def comparePlayers(listsOfPlayers, player1, player2):

    if player1 <= player2:
        return player1
    else:
        return player2

    # if listsOfPlayers[player1]["wins"] > listsOfPlayers[player2]["wins"]:
    #     return player1
    # elif listsOfPlayers[player2]["wins"] > listsOfPlayers[player2]["wins"]:
    #     return player2
    # else:
    #     if listsOfPlayers[player1]["draws"] > listsOfPlayers[player2]["draws"]:
    #         return player1
    #     elif listsOfPlayers[player2]["draws"] > listsOfPlayers[player2]["draws"]:
    #         return player2
    #     else:
    #         if listsOfPlayers[player1]["loses"] >= listsOfPlayers[player2]["loses"]:
    #             return player1
    #         else: # listsOfPlayers[player2]["loses"] > listsOfPlayers[player2]["loses"]:
    #             return player2

#Method creates a new group in the dictionary
#Group does not have any players when returning the dictionary
def createGroup(name, dictionary):

    dictionary[name] = {}
    dictionary[name]["players"] = []

    return dictionary

#Method creates a new user in the dictionary
def createUser(ctx, name, dictionary):

    if name in dictionary[userList]:
        return None
    else:
        dictionary[userList][name] = {}
        dictionary[userList][name]["name"] = name
        dictionary[userList][name]["wins"] = 0
        dictionary[userList][name]["draws"] = 0
        dictionary[userList][name]["loses"] = 0
        return dictionary

#Method initializes new embed
def initializeEmbed(title=None, description=None, colour = discord.Colour.green()):

    newEmbed = discord.Embed(
        title = title,
        description = description,
        colour = colour
    )

    return newEmbed

#Method to merge for mergeSort
def merge(listOfPlayers, leftIndex, middle, rightIndex):

    copyList = listOfPlayers

    #Create temporary lists
    leftSide = []
    rightSide = []

    for i in range(leftIndex, middle + 1, 1):
        leftSide.append(listOfPlayers[i])
    for i in range(middle + 1, rightIndex + 1, 1):
        rightSide.append(listOfPlayers[i])

    #Merge the lists together
    n1 = 0
    n2 = 0

    while n1 < len(leftSide) and n2 < len(rightSide):
        higherPlayer = comparePlayers(listOfPlayers, leftSide[n1], rightSide[n2])

        if higherPlayer == leftSide[n1]:
            copyList[leftIndex + n1 + n2] = leftSide[n1]
            n1 += 1
        else:
            copyList[leftIndex + n1 + n2] = rightSide[n2]
            n2 += 1
    
    #Add remaining leftside
    while n1 < len(leftSide):
        copyList[leftIndex + n1 + n2] = leftSide[n1]
        n1 += 1

    #Add remaining rightside
    while n2 < len(rightSide):
        copyList[leftIndex + n1 + n2] = rightSide[n2]
        n2 += 1

    return copyList

#Method merges 2 player lists together in hierarchy
def mergeSortPlayers(listOfPlayers, leftIndex, rightIndex):
    

    #When index meet each other, return
    if leftIndex >= rightIndex:
        return listOfPlayers
    
    middle = (int)((leftIndex + rightIndex) / 2)

    #Left
    listOfPlayers = mergeSortPlayers(listOfPlayers, leftIndex, middle)
    #Right
    listOfPlayers = mergeSortPlayers(listOfPlayers, middle + 1, rightIndex)

    #Merge
    return merge(listOfPlayers, leftIndex, middle, rightIndex)

#Method retrieves information from filename
def readFileInfo(filename):

    with open(filename, "r") as file:
        fileInfo = json.load(file)
        file.close()
    
    return fileInfo

#Method creates one sentence from retrieved input
def retrieveArgs(args):

    target = args[0]
    for i in range(1, len(args), 1):
        target += " " + args[i]
    
    return target

def updateGroupPlayer(dictionary, player, win, draw, lose):
    pass

#Method writes information to filename
def writeFileInfo(filename, information):

    with open(filename, "w") as file:
        json.dump(information, file)


#SECTION FOR TODO CODE!
#--------------------------------------------------------------------------------------------------#

#Command to test commands to be implemented
@client.command()
async def test(ctx, *, message):

    embed = initializeEmbed(title="Hello", description="nevermind")

    await ctx.send(embed=embed)

    # while True:

    #     def checker(reaction, user):
    #         return reaction.message.id == ctx.message.id

    #     try:
    #         reaction, user = await client.wait_for("reaction_add", check=checker, timeout=None)
    #     except:
    #         print("sth went wrong oops")
    #     else:
    #         print(str(reaction.emoji))

    # listOfNumbers = [22, 15, 48, 37, 33, 39, 68, 1, 22, 25]
    # sortedList = mergeSortPlayers(listOfNumbers, 0, len(listOfNumbers) - 1)
    # print(sortedList)

    # print(client.guilds)
    #[<Guild id=727953707114692618 name='PRPD_Bot development' shard_id=None chunked=False member_count=6>]

#Command which enables the user to make an announcement
@client.command()
async def announce(ctx, *, message):

    try:
        attachment = await ctx.message.attachments[0].to_file()
        await ctx.send(message, file=attachment)
    except: #The announcement does not contain an image
        await ctx.send(message)

client.run(TOKEN)