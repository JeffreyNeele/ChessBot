import discord
from discord.ext import commands

#Class defines emoji commands and methods
class ReactionEmojis():

    #Emotes to go through pages
    __firstPageEmote = "⏪"
    __lastPageEmote = "◀️"
    __nextPageEmote = "▶️"
    __endPageEmote = "⏩"
    __emojisPages = [__firstPageEmote, __lastPageEmote, __nextPageEmote, __endPageEmote]

    #Emotes for yes/no answers
    __yesEmote = "🇾"
    __noEmote = "🇳"
    __emojisAnswers = [__yesEmote, __noEmote]

    #Emotes to go through 1-10 options
    __oneEmote = "1️⃣"
    __twoEmote = "2️⃣"
    __threeEmote = "3️⃣"
    __fourEmote = "4️⃣"
    __fiveEmote = "5️⃣"
    __sixEmote = "6️⃣"
    __sevenEmote = "7️⃣"
    __eightEmote = "8️⃣"
    __nineEmote = "9️⃣"
    __tenEmote = "🔟"
    __emojiNumbers = [__oneEmote, __twoEmote, __threeEmote, __fourEmote, __fiveEmote, __sixEmote, __sevenEmote, __eightEmote, __nineEmote, __tenEmote]

    #Emotes to give wins/draws/loses to players
    __winUp = "✅" 
    __winDown = "❎"
    __drawUp = "⬜"
    __drawDown = "🔳"
    __loseUp = "❤️"
    __loseDown = "💔"
    __emojiWinDrawLose = [__winUp, __winDown, __drawUp, __drawDown, __loseUp, __loseDown]

    def __init__(self):
        pass

    #Method adds emojis to a message
    async def addEmojis(self, emojiList, message):

        for emoji in emojiList:
            await message.add_reaction(emoji)

    #Returns emojiPages
    def getPageEmojis(self):
        return self.__emojisPages
    
    #Returns description of emojis in emojiPages
    def descriptionPageEmojis(self):
        return "To first page: " + self.__firstPageEmote + " | last page: " + self.__lastPageEmote + " | next page: " + self.__nextPageEmote + " | to last page: " + self.__lastPageEmote

    #Processes the emojis in emojiPages to values
    def processPageEmoji(self, emoji, currentPage, maxPageNr):

        if emoji == self.__firstPageEmote:
            return 0
        elif emoji == self.__lastPageEmote and currentPage > 0:
            return currentPage - 1
        elif emoji == self.__nextPageEmote and currentPage < maxPageNr:
            return currentPage + 1
        elif emoji == self.__endPageEmote:
            return maxPageNr
        else:
            return currentPage

    #Returns emojiAnswers
    def getAnswerEmojis(self):
        return self.__emojisAnswers

    #Returns description of emojis in emojiAnswers
    def descriptionAnswerEmojis(self):
        return "Yes: " + self.__yesEmote + " | No: " + self.__noEmote

    #Process the emojis in emojiAnswers to True/False
    def processAnswerEmoji(self, emoji):

        if emoji == self.__yesEmote:
            return True
        else:
            return False
    
    #Returns emojiNumbers
    def getNumberEmojis(self):
        return self.__emojiNumbers

    #Returns description of emojis in emojiNumbers
    def descriptionNumerEmojis(self):
        return "React with 1 through 10 to pick one of the 10 options"

    #Process the emojis in emojiNumbers to the index of the emoji
    def processNumberEmoji(self, emoji):
        return self.__emojiNumbers.index(emoji)

    #Returns emojiWinDrawLose
    def getWinDrawLoseEmojis(self):
        return self.__emojiWinDrawLose
    
    #Returns description of emojis in emojiWinDrawLose
    def descriptionWinDrawLoseEmojis(self):
        return "add/delete Win: " + self.__winUp + "/" + self.__winDown + " | add/delete Draw: " + self.__drawUp + "/" + self.__drawDown + " | add/delete Lose: " + self.__loseUp + "/" + self.__loseDown

    #Process the emojis in emojiWinDrawLose to values for win/draw/lose
    def processWinDrawLoseEmoji(self, emoji):

        win = 0
        draw = 0
        lose = 0

        if emoji == self.__winUp:
            win = 1
        elif emoji == self.__winDown:
            win = -1
        elif emoji == self.__drawUp:
            draw = 1
        elif emoji == self.__drawDown:
            draw = -1
        elif emoji == self.__loseUp:
            lose = 1
        else:
            lose = -1
        
        return win, draw, lose