from datetime import datetime
from dataclasses import dataclass
import discord

# TODO: need some validation here for the strings below, so they can't just be random characters?
@dataclass
class Player:
    position:str # 'W1', 'W2', ... , 'L1', 'L2', ...
    characterName:str # 'lucent', 'chonk', 'alaxel', etc...
    characterClass:str
    isDead:int # 0=alive

class Fight:
    id:int
    modified:int
    guildId:int
    channelId:int
    date:datetime
    filePath:str
    sword:str
    players:list[Player]

    def __init__(self, id:int, modified:int, guildId:int, channelId:int, date:datetime, filePath:str, sword:str, players:list[Player]):
        self.id = id
        self.modified = modified
        self.guildId = guildId
        self.channelId = channelId
        self.date = date
        self.filePath = filePath
        self.sword = sword
        self.players = players
    
    def getEmbed(self, iconUrl:str, attachImage:bool=False):
        """
        creates a discord embed object ready to send to a discord channel.
        returns tuple of (embed, imageFile)
        imageFile = None if attackImage==False
        """
        # format winners and losers group:
        winners = ''
        losers = ''
        for p in self.players:
            deadText = ''
            swordText = ''
            if p.isDead:
                deadText = '*'
            if p.position.upper() == self.sword.upper():
                swordText = ' [A]'
            if (p.position[0].upper() == "W"):
                winners = winners + f"{p.position[1]}. ({p.characterClass}) {p.characterName}{deadText}{swordText}\n"
            else:
                losers = losers + f"{p.position[1]}. ({p.characterClass}) {p.characterName}{deadText}{swordText}\n"
        
        # check to see if there were no losers (could be none if there was no def)
        if losers == '':
            losers = 'None'

        modifiedStr = ''
        if self.modified != 0:
            modifiedStr = '*'

        # format the rest of the embed object
        embed = discord.Embed(color=0xf5f2ca)
        embed.add_field(name='Winners', value=winners, inline=True)
        embed.add_field(name='Losers', value=losers, inline=True)
        embed.set_author(name=f"ID: {self.id}{modifiedStr} ({self.date.strftime('%Y-%m-%d')})", icon_url=iconUrl)
        embed.set_footer(text=f"* = character is dead.\n[A] = Attacker")

        imgFile = None
        if attachImage:
            # prep the image to send
            imgFile = discord.File(self.filePath, filename='fight.png')
            embed.set_image(url='attachment://fight.png')

        return (embed, imgFile)
    
    # def toList(self) -> list:
    #     """
    #     this is supposed to mirror the "fromQueryResult" and turn this fight object into a flat list to be stored somewhere
    #     """
    #     result = list()
    #     result.append(self.id)
    #     result.append(self.modified)
    #     result.append(self.guildId)
    #     result.append(self.channelId)
    #     if self.date is None:
    #         result.append(None)
    #     else:
    #         result.append(int(self.date.timestamp()))
    #     result.append(self.filePath)
    #     result.append(self.sword)

    #     # now add the next 30 items from the players
    #     # (i know this isn't the most efficient way to loop through these, but who cares)
    #     # loop thru all player positions
    #     positions = ['w1', 'w2', 'w3', 'w4', 'w5', 'l1', 'l2', 'l3', 'l4', 'l5']
    #     for pos in positions:
    #         positionFilled = False
    #         # loop thru list of players to see if any are in this position
    #         for p in self.players:
    #             # if there is a player in this position, add stuff to the result object
    #             if p.position.lower() == pos:
    #                 positionFilled = True
    #                 result.append(p.characterName)
    #                 result.append(p.characterClass)
    #                 result.append(p.isDead)
    #                 break
    #         # if no player is in this position, fill with None objects
    #         if not positionFilled:
    #             result.append(None)
    #             result.append(None)
    #             result.append(None)
        
    #     # return the big list thing
    #     return result

    # def fromQueryResult(result:list):
    #     """
    #     create a Fight object from a tuple from SQL query results
    #     tuple looks like:
    #     (
    #         fight_id,
    #         modified,
    #         guild_id,
    #         channel_id,
    #         date,
    #         file_path,
    #         sword,
    #         w1_name,
    #         w1_class,
    #         w1_isdead,
    #         w2_
    #         ...
    #         l1_name,
    #         l1_class,
    #         l1_isdead,
    #         l2_
    #         ...
    #     )

    #     TODO: hmm... this should be renamed? I can use this to make a Fight object from any list,
    #     either from SQL result or from json read? I think?
    #     """
    #     # the order of objects in the tuple is defined by the way the database is set up
    #     (fight_id,
    #     modified,
    #     guild_id,
    #     channel_id,
    #     date,
    #     file_path,
    #     sword) = result[0:7]

    #     # handle if date is None
    #     if date is None:
    #         date = 0

    #     # parse the players from the last 30 parts of the tuple...
    #     players = []
    #     positions = ['w1', 'w2', 'w3', 'w4', 'w5', 'l1', 'l2', 'l3', 'l4', 'l5']
    #     p = 0
    #     for i in range(7, 36, 3):
    #         # print(i)
    #         if result[i] is None:
    #             p += 1
    #             continue
    #         players.append(Player(positions[p], result[i], result[i+1], result[i+2]))
    #         p += 1
        
    #     return Fight(fight_id, modified, guild_id, channel_id, datetime.fromtimestamp(date), file_path, sword, players)
