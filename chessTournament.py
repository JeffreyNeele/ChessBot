import filehandler
import globalFunctions
import reactionEmojis as reactEmoji
import math
import random

import discord
from discord.ext import commands

#Variables for file paths
usersFile = "users.json"
groupsFile = "groups.json"

#Variables for users.json indexing
userList = "users"
groupsList = "groups"

#Class defines commands and methods regarding creating the chess tournament
class ChessTournament(commands.Cog):

    emojiHandler = reactEmoji.ReactionEmojis()
    globalHandler = globalFunctions.Globals()

    def __init__(self, client):
        self.client = client
        self.__createNecessaryFiles()

    @commands.Cog.listener()
    async def on_ready(self):
        print("ChessTournament Cog is ready")

    ####################################################################################################
    #                                                                                                  #
    # COMMANDS                                                                                         #
    #                                                                                                  #
    ####################################################################################################

    # signup: Command lets a user sign up for the competition
    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def signup(self, ctx, *, target):

        #Get current player list
        usersInfo = filehandler.readFileInfo(usersFile)
        
        #Add new player to the list
        updatedList = self.__createUser(target, usersInfo[userList])

        if updatedList is None:
            await ctx.send(target + " is already signed up")
        else:
            #Update users.json
            usersInfo[userList] = updatedList
            filehandler.writeFileInfo(usersFile, usersInfo)

            await ctx.send(target + " is signed in!")

    # signout: Command lets a user sign out of the competition
    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def signout(self, ctx, *, target):

        usersInfo = filehandler.readFileInfo(usersFile)
        
        if target in usersInfo[userList]:
            del usersInfo[userList][target]
            await ctx.send(target + " is removed from the players list")
        else:
            await ctx.send(target + " is not an existant player")
        
        filehandler.writeFileInfo(usersFile, usersInfo)
    
    # allPlayers: Command shows all players in users.json (all signed up players)
    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def players(self, ctx):

        #Get players
        usersInfo = filehandler.readFileInfo(usersFile)

        if not bool(usersInfo[userList]):
            await ctx.send("No players available to show")
            return
        
        #Variables to create embed fields
        userKeys = list(usersInfo[userList].keys())
        page = 0
        shownPlayers = 10
        maxPage = math.floor((len(userKeys) - 1) / shownPlayers)
        lowAmount = page * shownPlayers
        maxAmount = lowAmount + shownPlayers

        #Initialize embed, which makes a nice looking window
        embedPlayers = self.globalHandler.initializeEmbed(title="Player list", description="List of all players")
        embedPlayers.set_footer(text="page: " + str(page + 1) + " of " + str(maxPage + 1))

        #Create embed field
        nameField = "Players"
        valueField = ""

        #Check if current page is not max page
        if maxAmount < len(userKeys):
            maxRange = maxAmount
        else: #max page
            maxRange = len(userKeys)

        for i in range(lowAmount, maxRange, 1):
            valueField += f'{i + 1}' + ": " + usersInfo[userList][userKeys[i]]["name"] + "\n"
        embedPlayers.add_field(name=nameField, value=valueField, inline=False)

        sendEmbed = await ctx.send(embed=embedPlayers)

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

                    lowAmount = page * shownPlayers
                    maxAmount = lowAmount + shownPlayers

                    embedPlayers.set_footer(text="page: " + str(page + 1) + " of " + str(maxPage + 1))
                    embedPlayers.clear_fields()

                    valueField = ""

                    #Check if current page is not max page
                    if maxAmount < len(userKeys):
                        maxRange = maxAmount
                    else: #max page
                        maxRange = len(userKeys)
                        
                    for i in range(lowAmount, maxRange, 1):
                        valueField += f'{i + 1}' + ": " + usersInfo[userList][userKeys[i]]["name"] + "\n"
                    embedPlayers.add_field(name=nameField, value=valueField, inline=False)

                    #Edit embed message
                    await sendEmbed.edit(embed=embedPlayers)

                #Delete emoji, but only when not in DM Channel (because DM channel does not allow that)
                if ctx.message.channel.type != discord.ChannelType.private:
                    await sendEmbed.remove_reaction(reaction.emoji, ctx.message.author)

    # groups: Command shows all the groups
    @commands.command()
    async def groups(self, ctx):
        
        groupsInfo = filehandler.readFileInfo(groupsFile)[groupsList]
        
        #Check if there are groups available
        if not bool(groupsInfo):
            await ctx.send("At the moment there are no groups available to show")
            return
        
        groupListKeys = list(groupsInfo.keys())

        page = 0
        maxPage = len(groupListKeys) - 1

        #Initialize embed, which makes a nice looking window
        embedGroups = self.globalHandler.initializeEmbed(title=groupListKeys[page], description="All players in " + groupListKeys[page])
        embedGroups.set_footer(text="page: " + str(page + 1) + " of " + str(maxPage + 1))

        nameFieldPlayers = "Players"
        valueFieldPlayers = ""

        nameFieldWinDrawLose = "Win/Draw/Lose"
        valueFieldWinDrawLose = ""

        #Add first page to the embed
        playersInGroup = groupsInfo[groupListKeys[page]]["players"]
        playersInGroupKeys = list(playersInGroup.keys())

        for i in range(0, len(playersInGroup), 1):
            #Add playerlist
            valueFieldPlayers += f"{i + 1}" + ": " + playersInGroup[playersInGroupKeys[i]]["name"] + "\n"

            #Add win/draws/loses
            valueFieldWinDrawLose += str(playersInGroup[playersInGroupKeys[i]]["wins"]) + " - " + str(playersInGroup[playersInGroupKeys[i]]["draws"]) + " - " + str(playersInGroup[playersInGroupKeys[i]]["loses"]) + "\n"
        
        embedGroups.add_field(name=nameFieldPlayers, value=valueFieldPlayers, inline=True)
        embedGroups.add_field(name=nameFieldWinDrawLose, value=valueFieldWinDrawLose, inline=True)
        sendEmbed = await ctx.send(embed=embedGroups)

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
            else:

                newPage = self.emojiHandler.processPageEmoji(reaction.emoji, page, maxPage)
                if page != newPage:
                    page = newPage

                    embedGroups.set_footer(text="page: " + str(page + 1) + " of " + str(maxPage + 1))

                    #Initialize embed, which makes a nice looking window
                    embedGroups.title = groupListKeys[page]
                    embedGroups.description = "All players in " + groupListKeys[page]
                    embedGroups.set_footer(text="page: " + str(page + 1) + " of " + str(maxPage + 1))
                    embedGroups.clear_fields()

                    valueFieldPlayers = ""
                    valueFieldWinDrawLose = ""

                    #Add first page to the embed
                    playersInGroup = groupsInfo[groupListKeys[page]]["players"]
                    playersInGroupKeys = list(playersInGroup.keys())

                    for i in range(0, len(playersInGroup), 1):
                        #Add playerlist
                        valueFieldPlayers += f"{i + 1}" + ": " + playersInGroup[playersInGroupKeys[i]]["name"] + "\n"

                        #Add win/draws/loses
                        valueFieldWinDrawLose += str(playersInGroup[playersInGroupKeys[i]]["wins"]) + " - " + str(playersInGroup[playersInGroupKeys[i]]["draws"]) + " - " + str(playersInGroup[playersInGroupKeys[i]]["loses"]) + "\n"
                    
                    embedGroups.add_field(name=nameFieldPlayers, value=valueFieldPlayers, inline=True)
                    embedGroups.add_field(name=nameFieldWinDrawLose, value=valueFieldWinDrawLose, inline=True)

                    #Edit embed message
                    await sendEmbed.edit(embed=embedGroups)

                #Delete emoji, but only when not in DM Channel (because DM channel does not allow that)
                if ctx.message.channel.type != discord.ChannelType.private:
                    await sendEmbed.remove_reaction(reaction.emoji, ctx.message.author)

    # createtourney: Command creates new competition
    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def createtourney(self, ctx, groupAmount):

        groupsInfo = filehandler.readFileInfo(groupsFile)

        #Check if a current tournament is setup
        if bool(groupsInfo[groupsList]):

            #Check if the user is confident in creating a new tourney, thus overiding the old tournament information
            confidenceCheckMessage = await ctx.send("There already is a current competition.\nAre you sure you want to create a new one?")

            #Add emojis
            await self.emojiHandler.addEmojis(self.emojiHandler.getAnswerEmojis(), confidenceCheckMessage)

            def checkConfidence(reaction, user):
                return reaction.emoji in self.emojiHandler.getAnswerEmojis() and reaction.message.id == confidenceCheckMessage.id and user == ctx.message.author

            #Wait for user reaction. Only break the while loop if the user reacted with yes
            while True:
                try:
                    reaction, user = await self.client.wait_for("reaction_add", check=checkConfidence, timeout=20)
                except:
                    await confidenceCheckMessage.edit(content="Sorry, you are timed out. Please try again!")
                    return
                else:

                    if self.emojiHandler.processAnswerEmoji(reaction.emoji):
                        break
                    else:
                        await confidenceCheckMessage.edit(content="Ok, I will not create a new tournament")
                        return
                    

        #Get players
        usersInfo = filehandler.readFileInfo(usersFile)
        allUsers = usersInfo[userList]

        if math.floor(len(allUsers) / int(groupAmount)) < 2:
            try:
                await confidenceCheckMessage.edit(content="Sorry, cannot create groups with atleast 2 players. Please either add more players or reduce amount of groups.")
            except:
                await ctx.send("Sorry, cannot create groups with atleast 2 players. Please either add more players or reduce amount of groups.")
            finally:
                return

        #Create variables for groups.json
        groupsInfo = {}
        groupsInfo[groupsList] = {}
        
        #Create the groups
        groupAmount = int(groupAmount)

        for nr in range(1, groupAmount + 1, 1):
            groupName = "Group " + str(nr)
            groupsInfo[groupsList] = self.__createGroup(groupName, groupsInfo[groupsList])

        listOfKeys = list(allUsers.keys())

        #Fill the groups
        while bool(listOfKeys):

            #Fill the groups in order, but choose the player randomly
            #iterating in order allows for equal distribution of players
            for nr in range(1, groupAmount + 1, 1):
                if not bool(listOfKeys): #No players left to add
                    break
                else:
                    playerChoice = random.choice(listOfKeys)
                    listOfKeys.remove(playerChoice)
                    player = allUsers[playerChoice]

                    groupName = "Group " + str(nr)
                    groupsInfo[groupsList][groupName]["players"][playerChoice] = player
        
        filehandler.writeFileInfo(groupsFile, groupsInfo)

        try:
            await confidenceCheckMessage.edit(content="Tournament is all set up")
        except:
            await ctx.send("Tournament is all set up")
        finally:
            await self.groups(ctx)

    # changestats: Command enables user to change the stats from players in the tournament
    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def changestats(self, ctx):

        groupsInfo = filehandler.readFileInfo(groupsFile)
        allGroups = groupsInfo[groupsList]

        if not bool(allGroups):
            await ctx.send("There currently is no competition available to showcase")
            return

        allPlayers = {}

        for groups in allGroups:
            playersInGroup = allGroups[groups]["players"]

            for player in playersInGroup:
                namePlayer = playersInGroup[player]["name"]
                wins = playersInGroup[player]["wins"]
                draws = playersInGroup[player]["draws"]
                loses = playersInGroup[player]["loses"]

                allPlayers[namePlayer] = {"name" : namePlayer, "group" : groups, "wins" : wins, "draws" : draws, "loses" : loses}

        playerListKeys = list(allPlayers)

        page = 0
        shownPlayers = 10
        maxPage = math.floor((len(allPlayers) - 1) / shownPlayers)

        #Initialize embed to show all the players
        embedPlayerslist = self.globalHandler.initializeEmbed(title="Player list", description="Choose the player you want to change the stats for\nusing emoticons 1 through 10")
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
        if maxPlayer < len(playerListKeys):
            maxRange = maxPlayer
        else:
            maxRange = len(playerListKeys)

        for i in range(lowPlayer, maxRange, 1):
            valueFieldPlayers += f"{i + 1}" + ": " + playerListKeys[i] + "\n"
            valueFieldGroups += allPlayers[playerListKeys[i]]["group"] + "\n"
            valueFieldWinDrawLose += str(allPlayers[playerListKeys[i]]["wins"]) + " - " + str(allPlayers[playerListKeys[i]]["draws"]) + " - " + str(allPlayers[playerListKeys[i]]["loses"]) + "\n"

        embedPlayerslist.add_field(name=nameFieldPlayers, value=valueFieldPlayers, inline=True)
        embedPlayerslist.add_field(name=nameFieldGroups, value=valueFieldGroups, inline=True)
        embedPlayerslist.add_field(name=nameFieldWinDrawLose, value=valueFieldWinDrawLose, inline=True)

        #Initialize embed to show the player stats
        embedPlayerChange = self.globalHandler.initializeEmbed(title="No player selected", description="please choose a player in the previous section")
        embedPlayerChange.set_footer(text=self.emojiHandler.descriptionWinDrawLoseEmojis())

        playerListEmbed = await ctx.send(embed=embedPlayerslist)
        playerEmbed = await ctx.send(embed=embedPlayerChange)

        #Add emotes
        await self.emojiHandler.addEmojis(self.emojiHandler.getPageEmojis() , playerListEmbed)
        await self.emojiHandler.addEmojis(self.emojiHandler.getNumberEmojis(), playerListEmbed)
        await self.emojiHandler.addEmojis(self.emojiHandler.getWinDrawLoseEmojis(), playerEmbed)

        def checkReaction(reaction, user):
            if not user.guild_permissions.administrator:
                return False
            elif reaction.message.id == playerListEmbed.id and (reaction.emoji in self.emojiHandler.getPageEmojis() or reaction.emoji in self.emojiHandler.getNumberEmojis()):
                return True
            elif reaction.message.id == playerEmbed.id and reaction.emoji in self.emojiHandler.getWinDrawLoseEmojis():
                return True
            else:
                return False

        selectedPlayer = ""

        while True:

            try:
                reaction, user = await self.client.wait_for("reaction_add", check=checkReaction, timeout=None)
            except:
                print("Oops, something went wrong")
            else:
                if reaction.emoji in self.emojiHandler.getPageEmojis():
                    newPage = self.emojiHandler.processPageEmoji(reaction.emoji, page, maxPage)
                    
                    if page != newPage:
                        page = newPage

                        embedPlayerslist.clear_fields()
                        embedPlayerslist.set_footer(text="page: " + str(page + 1) + " of " + str(maxPage + 1))
                        
                        lowPlayer = page * shownPlayers
                        maxPlayer = lowPlayer + shownPlayers

                        valueFieldPlayers = ""
                        valueFieldGroups = ""
                        valueFieldWinDrawLose = ""

                        #Add new page to the embed
                        if maxPlayer < len(playerListKeys):
                            maxRange = maxPlayer
                        else:
                            maxRange = len(playerListKeys)

                        for i in range(lowPlayer, maxRange, 1):
                            valueFieldPlayers += f"{i + 1}" + ": " + playerListKeys[i] + "\n"
                            valueFieldGroups += allPlayers[playerListKeys[i]]["group"] + "\n"
                            valueFieldWinDrawLose += str(allPlayers[playerListKeys[i]]["wins"]) + " - " + str(allPlayers[playerListKeys[i]]["draws"]) + " - " + str(allPlayers[playerListKeys[i]]["loses"]) + "\n"

                        embedPlayerslist.add_field(name=nameFieldPlayers, value=valueFieldPlayers, inline=True)
                        embedPlayerslist.add_field(name=nameFieldGroups, value=valueFieldGroups, inline=True)
                        embedPlayerslist.add_field(name=nameFieldWinDrawLose, value=valueFieldWinDrawLose, inline=True)

                        #Edit fields and remove reaction
                        await playerListEmbed.edit(embed=embedPlayerslist)

                    #Delete emoji, but only when not in DM Channel (because DM channel does not allow that)
                    if ctx.message.channel.type != discord.ChannelType.private:
                        await playerListEmbed.remove_reaction(reaction.emoji, ctx.message.author)
                
                elif reaction.emoji in self.emojiHandler.getNumberEmojis():
                    indexEmoji = self.emojiHandler.processNumberEmoji(reaction.emoji)

                    #Check if index will not succeed max amount of players, in the case no player is then selected
                    if indexEmoji + lowPlayer >= len(playerListKeys):
                        if ctx.message.channel.type != discord.ChannelType.private:
                            await playerListEmbed.remove_reaction(reaction.emoji, ctx.message.author)

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
                    if ctx.message.channel.type != discord.ChannelType.private:
                        await playerListEmbed.remove_reaction(reaction.emoji, ctx.message.author)
                #User changed stats from player
                else:   #reaction.emoji in emojiWinDrawLose

                    if selectedPlayer != "":
                        wins, draws, loses = self.emojiHandler.processWinDrawLoseEmoji(reaction.emoji)

                        if allPlayers[selectedPlayer]["wins"]  + wins >= 0:
                            allPlayers[selectedPlayer]["wins"] += wins
                        if allPlayers[selectedPlayer]["draws"] + draws >= 0:
                            allPlayers[selectedPlayer]["draws"] += draws
                        if allPlayers[selectedPlayer]["loses"] + loses >= 0:
                            allPlayers[selectedPlayer]["loses"] += loses

                        #Rebuild playerList
                        valueFieldPlayers = ""
                        valueFieldGroups = ""
                        valueFieldWinDrawLose = ""

                        for i in range(lowPlayer, maxRange, 1):
                            valueFieldPlayers += f"{i + 1}" + ": " + playerListKeys[i] + "\n"
                            valueFieldGroups += allPlayers[playerListKeys[i]]["group"] + "\n"
                            valueFieldWinDrawLose += str(allPlayers[playerListKeys[i]]["wins"]) + " - " + str(allPlayers[playerListKeys[i]]["draws"]) + " - " + str(allPlayers[playerListKeys[i]]["loses"]) + "\n"
                        
                        embedPlayerslist.clear_fields()
                        embedPlayerslist.add_field(name=nameFieldPlayers, value=valueFieldPlayers, inline=True)
                        embedPlayerslist.add_field(name=nameFieldGroups, value=valueFieldGroups, inline=True)
                        embedPlayerslist.add_field(name=nameFieldWinDrawLose, value=valueFieldWinDrawLose, inline=True)

                        #Rebuild playerChange
                        embedPlayerChange.clear_fields()
                        embedPlayerChange.add_field(name="Wins:", value=allPlayers[selectedPlayer]["wins"])
                        embedPlayerChange.add_field(name="Draws:", value=allPlayers[selectedPlayer]["draws"])
                        embedPlayerChange.add_field(name="Loses:", value=allPlayers[selectedPlayer]["loses"])

                        await playerEmbed.edit(embed=embedPlayerChange)
                        await playerListEmbed.edit(embed=embedPlayerslist)

                        #Update groups.json - user with changed stats and update order
                        playerGroup = allPlayers[selectedPlayer]["group"]
                        allGroups[playerGroup]["players"][selectedPlayer]["wins"] = allPlayers[selectedPlayer]["wins"]
                        allGroups[playerGroup]["players"][selectedPlayer]["draws"] = allPlayers[selectedPlayer]["draws"]
                        allGroups[playerGroup]["players"][selectedPlayer]["loses"] = allPlayers[selectedPlayer]["loses"]
                        listOfPlayers = []

                        for player in allGroups[playerGroup]["players"]:
                            listOfPlayers.append(allPlayers[player])
                        
                        listOfPlayers = self.__mergeSortPlayers(listOfPlayers, 0, len(listOfPlayers) - 1)
                        newGroup = {}
                        for player in listOfPlayers:
                            newGroup[player["name"]] = player
                        
                        allGroups[playerGroup]["players"] = newGroup
                        groupsInfo[groupsList] = allGroups
                        filehandler.writeFileInfo(groupsFile, groupsInfo)

                        
                    if ctx.message.channel.type != discord.ChannelType.private:
                        await playerEmbed.remove_reaction(reaction.emoji, ctx.message.author)

    # reset: deletes all users from users.json and all groups from groups.json
    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def reset(self, ctx):

        #Ask if the user is confident in deleting all the information
        confidenceCheckMessage = await ctx.send("Would you like to delete all users?")
        await self.emojiHandler.addEmojis(self.emojiHandler.getAnswerEmojis(), confidenceCheckMessage)

        #Check function - original author can only answer
        def checkConfidence(reaction, user):
                return reaction.emoji in self.emojiHandler.getAnswerEmojis() and reaction.message.id == confidenceCheckMessage.id and user == ctx.message.author

        try:
            reaction, user = await self.client.wait_for("reaction_add", check=checkConfidence, timeout=20)
        except:
            await ctx.send("Timed out. Please try again.")
            return
        else:   
            if self.emojiHandler.processAnswerEmoji(reaction.emoji):
                #users.json
                usersInfo = {}
                usersInfo[userList] = {}
                filehandler.writeFileInfo(usersFile, usersInfo)

                await confidenceCheckMessage.edit(content="Ok, I deleted all users.")
            else:
                await confidenceCheckMessage.edit(content="Ok, I will not delete the users.")
        
        confidenceCheckMessage = await ctx.send("Would you like to delete all current groups?")
        await self.emojiHandler.addEmojis(self.emojiHandler.getAnswerEmojis(), confidenceCheckMessage)

        try:
            reaction, user = await self.client.wait_for("reaction_add", check=checkConfidence, timeout=20)
        except:
            await ctx.send("Timed out. Please try again.")
            return
        else:
            if self.emojiHandler.processAnswerEmoji(reaction.emoji):
                #groups.json
                groupsInfo = {}
                groupsInfo[groupsList] = {}
                filehandler.writeFileInfo(groupsFile, groupsInfo)

                await confidenceCheckMessage.edit(content="Ok, I deleted all groups.")
            else:
                await confidenceCheckMessage.edit(content="Ok, I will not delete the groups.")

    ####################################################################################################
    #                                                                                                  #
    # ASSISTING METHODS                                                                                #
    #                                                                                                  #
    ####################################################################################################
    
    #Method which creates the files necessary to create a tournament (users.json and groups.json)
    def __createNecessaryFiles(self):
        
        #Create necessary files (if they are not present)
        #File with users
        try:
            usersInfo = filehandler.readFileInfo(usersFile)
        except:
            usersInfo = {}
            usersInfo[userList] = {}
            filehandler.writeFileInfo(usersFile, usersInfo)
        
        #File with groups
        try:
            groupsInfo = filehandler.readFileInfo(groupsFile)
        except:
            groupsInfo = {}
            groupsInfo[groupsList] = {}
            filehandler.writeFileInfo(groupsFile, groupsInfo)

    #Method creates a new user in the dictionary
    def __createUser(self, name, dictionary):

        if name in dictionary:
            return None
        else:
            dictionary[name] = {}
            dictionary[name]["name"] = name
            dictionary[name]["wins"] = 0
            dictionary[name]["draws"] = 0
            dictionary[name]["loses"] = 0
            return dictionary
    
    #Method creates a new group in the dictionary
    #Group does not have any players when returning the dictionary
    def __createGroup(self, name, dictionary):

        dictionary[name] = {}
        dictionary[name]["players"] = {}

        return dictionary

    #Method returns the player who is greater/superior/higher/...
    def __comparePlayers(self, listsOfPlayers, player1, player2):

        if player1["wins"] > player2["wins"]:
            return player1
        elif player2["wins"] > player1["wins"]:
            return player2
        else:
            if player1["draws"] > player2["draws"]:
                return player1
            elif player2["draws"] > player1["draws"]:
                return player2
            else:
                if player1["loses"] >= player2["loses"]:
                    return player1
                elif player2["loses"] > player1["loses"]:
                    return player2
                else:
                    if player1["name"] <= player2["name"]:
                        return player1
                    else:
                        return player2

    #Method to __merge for mergeSort
    def __merge(self, listOfPlayers, leftIndex, middle, rightIndex):

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
            higherPlayer = self.__comparePlayers(listOfPlayers, leftSide[n1], rightSide[n2])

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

    #Method merges 2 player lists together in the hierarchy
    def __mergeSortPlayers(self, listOfPlayers, leftIndex, rightIndex):
        
        #When index meet each other, return
        if leftIndex >= rightIndex:
            return listOfPlayers        
        middle = (int)((leftIndex + rightIndex) / 2)

        #Left
        listOfPlayers = self.__mergeSortPlayers(listOfPlayers, leftIndex, middle)
        #Right
        listOfPlayers = self.__mergeSortPlayers(listOfPlayers, middle + 1, rightIndex)
        #Merge
        return self.__merge(listOfPlayers, leftIndex, middle, rightIndex)

def setup(client):
    client.add_cog(ChessTournament(client))